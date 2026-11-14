"""C/C++ matched-slot projection differential against fixed instruction trace."""
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
spec=importlib.util.spec_from_file_location('update',HERE/'match_update.py'); update=importlib.util.module_from_spec(spec); spec.loader.exec_module(update)


def worker(dll):
    image=update.v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=update.v.SHA: raise ValueError('firmware identity mismatch')
    lib=ctypes.CDLL(str(dll)); word=ctypes.c_uint32; fn=lib.scheduler_match_projection
    fn.argtypes=[word]*6+[ctypes.POINTER(word)]; fn.restype=None; out=(word*15)()
    rng=random.Random(416001); count=0
    def check(index,old,mode,new,task,target):
        nonlocal count
        a0,a1,events=update.run(image,index,old,mode,new,task,target)
        if events[0]!=('read',update.BASE+index*12+8,4,old): raise ValueError('bad original read')
        extra=2 if old else 0
        if old and events[1:3]!=(('read',0x40068,4,target),('call',target,old)): raise ValueError('bad original call')
        gp,first,second=events[1+extra:]
        if gp!=('read','gp+166',1,task) or first[0]!='write' or second[0]!='write': raise ValueError('bad original events')
        expected=[a0,a1,events[0][1],events[0][3],int(old!=0),0x40068 if old else 0,target if old else 0,old if old else 0,gp[3],first[1],first[3],second[1],second[3],first[2],second[2]]
        fn(index,old,mode,new,task,target,out)
        if list(out)!=expected: raise ValueError(f'model mismatch index={index} old={old:#x} mode={mode:#x}')
        count+=1
    for mode in range(65536):
        # Distribute mode values across indices and old-argument cases; this
        # is not the Cartesian product of those inputs.
        check(mode%15,(0,1,0xffffffff)[mode%3],mode,(mode*65537)&0xffffffff,mode&255,0x12345678)
    for _ in range(20000):
        check(rng.randrange(15),rng.choice((0,rng.getrandbits(32)|1)),rng.getrandbits(32),rng.getrandbits(32),rng.randrange(256),rng.getrandbits(32))
    print(f'PASS: {count} C model comparisons, all 65536 low-16 mode values',flush=True)


def main():
    parser=argparse.ArgumentParser(); group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars',type=Path); group.add_argument('--worker',type=Path); args=parser.parse_args()
    if args.worker: worker(args.worker); return
    with tempfile.TemporaryDirectory(prefix='tsl9-match-') as temp:
        tmp=Path(temp); batch=tmp/'build.bat'
        def build(source,dll,flags):
            batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{source}" /Fe:"{dll}"\n@exit /b %errorlevel%\n',encoding='utf-8')
            subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=tmp,check=True)
        for label,flags in (('C','/TC /std:c11'),('C++','/TP /std:c++17')):
            dll=tmp/(label.replace('+','p')+'.dll'); build(HERE/'match_model.c',dll,flags)
            print(label+': ',end='',flush=True)
            subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)],check=True)
        text=(HERE/'match_model.c').read_text(encoding='utf-8')
        for name,old,new in (('call_condition','out[4] = old_argument != 0;','out[4] = old_argument == 0;'),('mode_width','out[10] = mode & UINT32_C(255);','out[10] = mode;'),('argument_slot','slot + UINT32_C(8); out[12]','slot + UINT32_C(4); out[12]'),('mask','UINT32_C(1) << index','UINT32_C(2) << index')):
            if text.count(old)!=1: raise ValueError('ambiguous mutant')
            source,dll=tmp/(name+'.c'),tmp/(name+'.dll'); source.write_text(text.replace(old,new),encoding='utf-8'); build(source,dll,'/TC /std:c11')
            proc=subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)],capture_output=True,text=True)
            if proc.returncode==0 or 'model mismatch' not in proc.stderr: raise ValueError(f'mutant not rejected: {name}')
            print(f'PASS: {name} mutant rejected',flush=True)
    print('Provider behavior beyond returning stub not modeled; no hardware execution.')

if __name__=='__main__': main()
