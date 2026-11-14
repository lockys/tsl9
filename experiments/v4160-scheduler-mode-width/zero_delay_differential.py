"""C/C++ zero-delay insertion model vs bounded original-instruction trace."""
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
spec=importlib.util.spec_from_file_location('zi',HERE/'zero_delay_insert.py'); zi=importlib.util.module_from_spec(spec); spec.loader.exec_module(zi)


def worker(dll):
    image=zi.v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=zi.v.SHA: raise ValueError('firmware identity mismatch')
    lib=ctypes.CDLL(str(dll)); word=ctypes.c_uint32; fn=lib.scheduler_zero_insert
    fn.argtypes=[word]*6+[ctypes.POINTER(word),ctypes.POINTER(word)]; fn.restype=None
    out=(word*23)(); rng=random.Random(0x4160)
    for n in range(30000):
        index=n%15; callback=rng.getrandbits(32); argument=rng.getrandbits(32); task=rng.randrange(256); target=rng.getrandbits(32)
        sp=(0xfffffff0 if n%100==0 else rng.getrandbits(30)*4); saved=[rng.getrandbits(32) for _ in range(6)]
        a0,a1,t1,endsp,regs,events=zi.run(image,index,callback,argument,task,target,sp,saved)
        for i,offset in enumerate((24,28,20,12,8)):
            if events[i]!=('read',(sp+offset)&0xffffffff,4,saved[i]): raise ValueError('stack read mismatch')
        if events[8]!=('read',(sp+16)&0xffffffff,4,saved[5]) or events[9]!=('read',0x40050,4,target) or events[10]!=('read','gp+166',1,task): raise ValueError('read order mismatch')
        if any(ev[0]!='write' for ev in events[5:8]): raise ValueError('write order mismatch')
        expected=[a0,a1,t1,endsp,*[regs[k] for k in ('s0','ra','s1','s3','s4','s2')],*events[5][1:],*events[6][1:],*events[7][1:],events[9][1],events[9][3],events[10][3],events[10][2]]
        fn(index,callback,argument,task,target,sp,(word*6)(*saved),out)
        if list(out)!=expected: raise ValueError(f'model mismatch case {n} index {index}')
    print('PASS: 30000 zero-delay C model comparisons, including stack pointer wrap',flush=True)


def main():
    parser=argparse.ArgumentParser(); group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars',type=Path); group.add_argument('--worker',type=Path); args=parser.parse_args()
    if args.worker: worker(args.worker); return
    with tempfile.TemporaryDirectory(prefix='tsl9-zero-') as temp:
        tmp=Path(temp); batch=tmp/'build.bat'
        def build(source,dll,flags):
            batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{source}" /Fe:"{dll}"\n@exit /b %errorlevel%\n',encoding='utf-8')
            subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=tmp,check=True)
        for label,flags in (('C','/TC /std:c11'),('C++','/TP /std:c++17')):
            dll=tmp/(label.replace('+','p')+'.dll'); build(HERE/'zero_delay_model.c',dll,flags)
            print(label+': ',end='',flush=True)
            subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)],check=True)
        text=(HERE/'zero_delay_model.c').read_text(encoding='utf-8')
        for name,old,new in (('mode','out[15] = 0;','out[15] = 1;'),('target','UINT32_C(0x40050)','UINT32_C(0x40058)'),('mask','UINT32_C(1) << index','UINT32_C(2) << index'),('sp','sp + UINT32_C(32)','sp + UINT32_C(16)')):
            if text.count(old)!=1: raise ValueError('ambiguous mutant')
            source,dll=tmp/(name+'.c'),tmp/(name+'.dll'); source.write_text(text.replace(old,new),encoding='utf-8'); build(source,dll,'/TC /std:c11')
            proc=subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)],capture_output=True,text=True)
            if proc.returncode==0 or 'model mismatch' not in proc.stderr: raise ValueError(f'mutant not rejected: {name}')
            print(f'PASS: {name} mutant rejected',flush=True)
    print('Assumed independent synthetic reads and no traps; no provider or physical execution.')

if __name__=='__main__': main()
