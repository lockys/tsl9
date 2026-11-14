"""Compare case-3 C event projection against bounded original-byte components."""
import argparse
import ctypes
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('case3',HERE/'case3_setter.py')
case3=importlib.util.module_from_spec(spec); spec.loader.exec_module(case3)


def worker(dll,mutant):
    image=case3.setter.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=case3.setter.SHA: raise ValueError('image identity')
    raw=image[0x1473e-0x8000:0x14746-0x8000]
    jump=image[0x14746-0x8000:0x14748-0x8000]
    u=ctypes.c_uint32; fn=ctypes.CDLL(str(dll)).tsl9_case3
    fn.argtypes=[u,u,u,ctypes.POINTER(u)]; fn.restype=None
    def compare(handle,first,second):
        target,a0,a1,_=case3.case.entry(0x1473e,raw,handle)
        if target!=0x13ba6: raise ValueError('call mismatch')
        _,writes,_=case3.setter.run(image,a0,a1,first,second)
        expected=[case3.jump(jump),0,0,0]
        if writes: expected=[case3.jump(jump),1,*writes[0]]
        out=(u*4)(); fn(handle,first,second,out)
        return list(out)==expected
    if mutant:
        if all(compare(*c) for c in ((5,5,5),(5,4,5),(5,4,4),(0x10005,5,5))): raise ValueError('mutant not detected')
        print('PASS: semantic mutant rejected',flush=True); return
    for first in range(65536):
        for handle,second in ((first,first),(first^1,first^1),(first^1,first),(first|0x10000,first)):
            if not compare(handle,first,second): raise ValueError('case mismatch')
    print('PASS: 262144 C vs original projection comparisons',flush=True)


def main():
    p=argparse.ArgumentParser(); g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--vcvars',type=Path); g.add_argument('--worker',type=Path); p.add_argument('--mutant',action='store_true'); a=p.parse_args()
    if a.worker: worker(a.worker,a.mutant); return
    src=(HERE/'case3_model.c').read_text(encoding='utf-8'); variants=[('base',src)]
    for name,old,new in (('value','out[3] = 4','out[3] = 3'),('first','0x2000c799','0x2000c798'),('second','0x2000c79d','0x2000c79c'),('width','handle == first','(handle & 0xffffu) == first')):
        if src.count(old)!=(2 if name=='value' else 1): raise ValueError('ambiguous mutant')
        variants.append((name,src.replace(old,new)))
    with tempfile.TemporaryDirectory(prefix='tsl9-case3-') as tmp:
        folder=Path(tmp)
        for label,flags in (('C','/TC /std:c11'),('Cpp','/TP /std:c++17')):
            for name,text in variants:
                source=folder/(label+name+'.c'); dll=folder/(label+name+'.dll'); batch=folder/'build.bat'; source.write_text(text,encoding='utf-8')
                batch.write_text(f'@call "{a.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{source}" /Fe:"{dll}"\n@exit /b %errorlevel%\n',encoding='utf-8')
                subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=folder,check=True)
                cmd=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)]
                if name!='base': cmd.append('--mutant')
                subprocess.run(cmd,check=True)
    print('Event projection only; successful memory access and leaf return assumed.')

if __name__=='__main__': main()
