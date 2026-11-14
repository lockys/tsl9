#!/usr/bin/env python3
"""Compare C event projection to fixed-byte TX projection; no CPU emulation."""
import argparse,ctypes,hashlib,importlib.util,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
s=importlib.util.spec_from_file_location('tx',HERE/'tx-copy-step.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def worker(dll,root,mutant):
    raw=(root/m.BIN).read_bytes();m.need(len(raw)==76800 and hashlib.sha256(raw).hexdigest()==m.SHA,'firmware identity')
    for pc,h in m.WINDOWS:
        b=bytes.fromhex(h);m.need(raw[pc-0x8000:pc-0x8000+len(b)]==b,'instruction bytes')
    u=ctypes.c_uint32;f=ctypes.CDLL(str(dll)).tx_copy_step;f.argtypes=[u]*6+[ctypes.POINTER(u)];f.restype=None
    def compare(i,n,src,dst,sum_,value):
        memory={(src+i)&m.MASK:value};pc,idx,cs,events=m.step(i,n,src,dst,sum_,memory)
        expected=[pc,idx,cs,0,0,0,0] if not events else [pc,idx,cs,1,events[0][1],events[1][1],value]
        out=(u*7)();f(i,n,src,dst,sum_,value,out);return list(out)==expected
    if mutant:
        cases=((0x10000,1,0xffffffff,0xfffffffc,255,2),(2,2,3,4,5,6),(0xffffffff,65536,0xffffffff,0xffffffff,0xffffffff,255))
        if all(compare(*x) for x in cases):raise ValueError('mutant survived')
        print('PASS: mutant rejected');return
    for low in range(65536):
        i=(low<<16)|low
        for n in (low,low+1):
            if not compare(i,n,0xffffffff,0xfffffffc,0xffffffff,low&255):raise ValueError('mismatch')
    print('PASS: 131072 C versus Python event comparisons')
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--vcvars',type=Path);g.add_argument('--worker',type=Path);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--mutant',action='store_true');a=p.parse_args()
    if a.worker:worker(a.worker,a.root,a.mutant);return
    src=(HERE/'tx_copy_step_model.c').read_text();variants=[('base',src)]
    for name,old,new in (('index_width','(index & 0xffffu) < length','index < length'),('target','dst + index + 5u','dst + index + 4u'),('checksum','(sum + value) & 255u','sum + value'),('increment','index + 1u','index + 2u')):
        if src.count(old)!=1:raise ValueError('ambiguous mutant')
        variants.append((name,src.replace(old,new)))
    with tempfile.TemporaryDirectory(prefix='tsl9-tx-step-') as tmp:
        d=Path(tmp)
        for lang,flags in (('C','/TC /std:c11'),('C++','/TP /std:c++17')):
            for name,text in variants:
                source=d/(name+'.c');dll=d/(name+'.dll');bat=d/'build.bat';source.write_text(text)
                bat.write_text(f'@call "{a.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{source}" /Fe:"{dll}"\n@exit /b %errorlevel%\n')
                subprocess.run(['cmd.exe','/d','/c',str(bat)],cwd=d,check=True)
                cmd=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll),'--root',str(a.root)]
                if name!='base':cmd.append('--mutant')
                subprocess.run(cmd,check=True);print(lang,name,'done',flush=True)
    print('LIMIT: both projections are manually derived; no target CPU, ABI, MMIO or hardware execution')
if __name__=='__main__':main()
