"""C/C++ full-table epilogue vs fixed original instruction projection."""
import argparse
import ctypes
import hashlib
import importlib.util
from pathlib import Path
import random
import subprocess
import sys
import tempfile
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('full_exit',HERE/'full_exit.py'); original=importlib.util.module_from_spec(spec); spec.loader.exec_module(original)


def worker(dll):
    image=original.v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=original.v.SHA: raise ValueError('firmware identity mismatch')
    lib=ctypes.CDLL(str(dll)); word=ctypes.c_uint32; fn=lib.scheduler_full_exit
    fn.argtypes=[word,word,ctypes.POINTER(word),ctypes.POINTER(word)]; fn.restype=None
    out=(word*16)(); rng=random.Random(416007)
    for n in range(70000):
        a0=(1,0,0xffffffff,rng.getrandbits(32))[n%4]
        sp=(0xfffffff0,0xfffffffc,0,0x1000,rng.getrandbits(30)*4)[n%5]
        saved=[rng.getrandbits(32) for _ in range(6)]
        value,dest,end,regs,events=original.run(image,sp,saved,a0)
        if any(event[0]!='read' or event[2]!=4 for event in events): raise ValueError('original read event mismatch')
        expected=[value,dest,end,*[regs[x] for x in ('s0','ra','s1','s2','s3','s4')],*[ev[1] for ev in events],4]
        fn(a0,sp,(word*6)(*saved),out)
        if list(out)!=expected: raise ValueError(f'full exit model mismatch case={n}')
    print('PASS: 70000 full-exit C projections including arbitrary a0 and stack wrap',flush=True)


def main():
    parser=argparse.ArgumentParser(); group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars',type=Path); group.add_argument('--worker',type=Path); args=parser.parse_args()
    if args.worker: worker(args.worker); return
    with tempfile.TemporaryDirectory(prefix='tsl9-full-exit-') as temp:
        tmp=Path(temp); batch=tmp/'build.bat'
        def build(source,dll,flags):
            batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{source}" /Fe:"{dll}"\n@exit /b %errorlevel%\n',encoding='utf-8')
            subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=tmp,check=True)
        for label,flags in (('C','/TC /std:c11'),('C++','/TP /std:c++17')):
            dll=tmp/(label.replace('+','p')+'.dll'); build(HERE/'full_exit_model.c',dll,flags)
            print(label+': ',end='',flush=True)
            subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)],check=True)
        text=(HERE/'full_exit_model.c').read_text(encoding='utf-8')
        for name,old,new in (('result','out[0]=a0;','out[0]=1;'),('return','out[1]=saved[1];','out[1]=saved[0];'),('stack','sp+UINT32_C(32)','sp+UINT32_C(16)'),('order','out[9]=sp+UINT32_C(28);','out[9]=sp+UINT32_C(24);')):
            if text.count(old)!=1: raise ValueError('ambiguous mutant')
            source,dll=tmp/(name+'.c'),tmp/(name+'.dll'); source.write_text(text.replace(old,new),encoding='utf-8'); build(source,dll,'/TC /std:c11')
            proc=subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)],capture_output=True,text=True)
            if proc.returncode==0 or 'full exit model mismatch' not in proc.stderr: raise ValueError(f'mutant not rejected: {name}')
            print(f'PASS: {name} mutant rejected',flush=True)
    print('Successful independent synthetic stack reads; no provider, traps or hardware execution.')

if __name__=='__main__': main()
