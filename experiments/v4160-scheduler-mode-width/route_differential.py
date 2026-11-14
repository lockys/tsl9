"""Differential test scheduler route model against bounded instruction segments.

Composition crosses explicit segment boundaries; no continuous CPU or hardware.
"""
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

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
precedence=load('dp',HERE/'delay_precedence.py')


def worker(dll):
    image=precedence.z.v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=precedence.z.v.SHA: raise ValueError('firmware identity mismatch')
    lib=ctypes.CDLL(str(dll)); word=ctypes.c_uint32; fn=lib.scheduler_route
    fn.argtypes=[word,word,ctypes.POINTER(word),ctypes.POINTER(word)]; fn.restype=None
    out=(word*2)(); count=0
    def check(words,callback,delay):
        nonlocal count
        if precedence.branch(image,delay)==0x913c:
            pc,idx,_,_=precedence.z.scan(image,words)
            if pc==0x914a: expected=(0,idx)
            else: expected=None
        else: expected=None
        if expected is None:
            callback_out,_,s2,_,_,a5=precedence.setup.run(image,callback,0x100,delay,0x12345678)
            if (callback_out,s2,a5)!=(callback,0x2000be08,0x2000be08): raise ValueError('setup mismatch')
            pc,idx,_,_=precedence.m.scan(image,words,callback)
            if pc==0x91a2: expected=(1,idx)
            else:
                pc,idx,_,_,_=precedence.m.free.scan(image,words)
                expected=(2,idx) if pc==0x920e else (3,15)
        fn(callback,delay,(word*15)(*words),out)
        if tuple(out)!=expected: raise ValueError(f'route model mismatch case={count} callback={callback:#x} delay={delay:#x}')
        count+=1
    # Enumerate all occupied patterns; occupied values alternate between a
    # matching key and another nonzero key, plus zero-callback probes.
    for bits in range(1<<15):
        words=[(0x1333c if i%2==0 else 0xabcdef01) if bits&(1<<i) else 0 for i in range(15)]
        for callback,delay in ((0x1333c,0),(0x1333c,300),(0,0),(0,1)):
            check(words,callback,delay)
    rng=random.Random(416003)
    for _ in range(10000):
        callback=rng.choice((0,1,0xffffffff,0x1333c)); delay=rng.choice((0,1,300,0xffffffff))
        check([rng.choice((0,callback,rng.getrandbits(32)|1)) for _ in range(15)],callback,delay)
    print(f'PASS: {count} route comparisons: exhaustive occupancy plus random duplicate keys',flush=True)


def main():
    parser=argparse.ArgumentParser(); group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars',type=Path); group.add_argument('--worker',type=Path); args=parser.parse_args()
    if args.worker: worker(args.worker); return
    with tempfile.TemporaryDirectory(prefix='tsl9-route-') as temp:
        tmp=Path(temp); batch=tmp/'build.bat'
        def build(source,dll,flags):
            batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{source}" /Fe:"{dll}"\n@exit /b %errorlevel%\n',encoding='utf-8')
            subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=tmp,check=True)
        for label,flags in (('C','/TC /std:c11'),('C++','/TP /std:c++17')):
            dll=tmp/(label.replace('+','p')+'.dll'); build(HERE/'route_model.c',dll,flags)
            print(label+': ',end='',flush=True)
            subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)],check=True)
        text=(HERE/'route_model.c').read_text(encoding='utf-8')
        for name,old,new in (('zero_delay','if (delay == 0)', 'if (delay != 0)'),('match','if (words[i] == callback)', 'if (callback != 0 && words[i] == callback)'),('bound','i < 15','i < 14'),('insert','out[0] = 2;','out[0] = 3;')):
            if name!='bound' and text.count(old)!=1: raise ValueError('ambiguous mutant')
            mutated=text.replace(old,new,1)
            source,dll=tmp/(name+'.c'),tmp/(name+'.dll'); source.write_text(mutated,encoding='utf-8'); build(source,dll,'/TC /std:c11')
            proc=subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)],capture_output=True,text=True)
            if proc.returncode==0 or 'route model mismatch' not in proc.stderr: raise ValueError(f'mutant not rejected: {name}')
            print(f'PASS: {name} mutant rejected',flush=True)
    print('Only stable synthetic table routing; provider, concurrency, traps and real hardware not executed.')

if __name__=='__main__': main()
