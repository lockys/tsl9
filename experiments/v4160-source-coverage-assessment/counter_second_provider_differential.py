#!/usr/bin/env python3
"""Host C and C++ comparison with pinned bounded instruction projection."""
import argparse,ctypes,hashlib,importlib.util,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('projection',HERE/'counter-precheck-second-provider.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def worker(dll,mutant,root):
    image=(root/m.BIN).read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=m.SHA:raise ValueError('APP identity')
    m.check(image[0xa9e:0xabe]);u=ctypes.c_uint32;f=ctypes.CDLL(str(dll)).counter_second_provider
    f.argtypes=[u,u,u,u,ctypes.POINTER(u)];f.restype=None
    def compare(gp,s2,target,result):
        c,pc,a2=m.project(gp,s2,target,result)
        expected=[0,0,0,0,0,pc,0] if c is None else [1,*c,pc,a2]
        out=(u*7)();f(gp,s2,target,result,out);return list(out)==expected
    if mutant:
        if all(compare(*v) for v in ((0,0xfffe,1,0),(0,1,1,1),(0xffffffff,2,1,0),(0,3,1,0x101))):raise ValueError('mutant survived')
        print('PASS: C semantic mutant rejected');return
    for h in range(65536):
        for result in (0,1,2,0xffffffff):
            if not compare((h+0xffff8000)&0xffffffff,h,(h<<16)|1,result):raise ValueError('differential mismatch')
    for h in (0x10000,0x1fffe,0xffffffff):
        if not compare(0xffffffff,h,0xffffffff,1):raise ValueError('full width mismatch')
    print('PASS: 262144 comparisons and 3 full-width boundaries')
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--vcvars',type=Path);g.add_argument('--worker',type=Path);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--mutant',action='store_true');a=p.parse_args()
    if a.worker:worker(a.worker,a.mutant,a.root);return
    src=(HERE/'counter_second_provider_model.c').read_text()
    variants=[('base',src)]
    for name,old,new in (('sentinel','s2 == 0xfffeu','s2 == 0xffffu'),('target','target & ~1u','target'),('argument','gp + 128u','gp + 127u'),('return','result == 1u','result == 0u'),('result_width','result == 1u','(result & 255u) == 1u')):
        if src.count(old)!=1:raise ValueError('ambiguous mutant '+name)
        variants.append((name,src.replace(old,new)))
    with tempfile.TemporaryDirectory(prefix='tsl9-second-provider-') as tmp:
        d=Path(tmp)
        for language,flags in (('C','/TC /std:c11'),('C++','/TP /std:c++17')):
            for name,text in variants:
                source=d/(name+'.c');dll=d/(name+'.dll');bat=d/'build.bat';source.write_text(text)
                bat.write_text(f'@call "{a.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{source}" /Fe:"{dll}"\n@exit /b %errorlevel%\n')
                subprocess.run(['cmd.exe','/d','/c',str(bat)],cwd=d,check=True)
                cmd=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll),'--root',str(a.root)]
                if name!='base':cmd.append('--mutant')
                subprocess.run(cmd,check=True);print(language,name,'done',flush=True)
    print('LIMIT: C event projection and Python fixed-byte projection; no target ABI or hardware validation')
if __name__=='__main__':main()
