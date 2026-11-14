"""C/C++ resident-exit projection vs fixed original instruction traces."""
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
spec=importlib.util.spec_from_file_location('exit',HERE/'resident_exit.py'); ex=importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)


def worker(dll):
    image=ex.v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=ex.v.SHA: raise ValueError('firmware identity mismatch')
    lib=ctypes.CDLL(str(dll)); word=ctypes.c_uint32; fn=lib.scheduler_resident_exit
    fn.argtypes=[word,word,word,ctypes.POINTER(word),word,word,ctypes.POINTER(word)]; fn.restype=None
    out=(word*20)(); rng=random.Random(416004); count=0
    def check(mode,result,sp):
        nonlocal count
        task=rng.getrandbits(32); target=rng.getrandbits(32); saved=[rng.getrandbits(32) for _ in range(6)]
        kind,dest,a0,end,regs,events=ex.run(image,mode,task,sp,saved,target,result)
        if kind=='tail':
            reads=events[:6]; pointer=events[6]
            flag,callarg,link=0,0,0
        else:
            pointer,call,*reads=events
            if call!=('call',target,task,0x9230): raise ValueError('original call event mismatch')
            flag,callarg,link=1,call[2],call[3]
        if pointer[0]!='read' or pointer[2:]!=(4,target) or any(x[0]!='read' or x[2]!=4 for x in reads): raise ValueError('original read event mismatch')
        expected=[int(kind=='tail'),dest,a0,end,*[regs[k] for k in ('s0','ra','s1','s2','s3','s4')],*[x[1] for x in reads],pointer[1],flag,callarg,link]
        fn(mode,task,sp,(word*6)(*saved),target,result,out)
        if list(out)!=expected: raise ValueError(f'resident model mismatch case={count} mode={mode:#x} result={result:#x}')
        count+=1
    for x in range(65536):
        check(0,x,0xfffffff0 if x&1 else 0x1000)
        check((x|0x10000),x,0xfffffff0 if x&1 else 0x1000)
    for _ in range(10000): check(rng.choice((0,1,0x100,0xffffffff)),rng.getrandbits(32),rng.getrandbits(30)*4)
    print(f'PASS: {count} resident-exit C comparisons; 65536 return values per route',flush=True)


def main():
    parser=argparse.ArgumentParser(); group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars',type=Path); group.add_argument('--worker',type=Path); args=parser.parse_args()
    if args.worker: worker(args.worker); return
    with tempfile.TemporaryDirectory(prefix='tsl9-resident-') as temp:
        tmp=Path(temp); batch=tmp/'build.bat'
        def build(source,dll,flags):
            batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{source}" /Fe:"{dll}"\n@exit /b %errorlevel%\n',encoding='utf-8')
            subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=tmp,check=True)
        for label,flags in (('C','/TC /std:c11'),('C++','/TP /std:c++17')):
            dll=tmp/(label.replace('+','p')+'.dll'); build(HERE/'resident_exit_model.c',dll,flags)
            print(label+': ',end='',flush=True)
            subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)],check=True)
        text=(HERE/'resident_exit_model.c').read_text(encoding='utf-8')
        for name,old,new in (('narrow_mode','out[0] = (mode != 0);','out[0] = ((mode & UINT32_C(255)) != 0);'),('return_test','(uint32_t)(result == 0)','(uint32_t)(result != 0)'),('pointer','UINT32_C(0x4022c)','UINT32_C(0x40058)'),('stack','sp + UINT32_C(32)','sp + UINT32_C(16)')):
            if text.count(old)!=1: raise ValueError('ambiguous mutant')
            source,dll=tmp/(name+'.c'),tmp/(name+'.dll'); source.write_text(text.replace(old,new),encoding='utf-8'); build(source,dll,'/TC /std:c11')
            proc=subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)],capture_output=True,text=True)
            if proc.returncode==0 or 'resident model mismatch' not in proc.stderr: raise ValueError(f'mutant not rejected: {name}')
            print(f'PASS: {name} mutant rejected',flush=True)
    print('Provider returns by assumption; no provider effects, aliasing, traps or hardware execution.')

if __name__=='__main__': main()
