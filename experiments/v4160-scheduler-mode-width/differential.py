"""C/C++ selected-slot scheduler projection vs fixed original instructions."""
import argparse
import ctypes
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('mode_verify',HERE/'verify.py')
verify=importlib.util.module_from_spec(spec); spec.loader.exec_module(verify)


def worker(dll):
    image=verify.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=verify.SHA: raise ValueError('firmware identity mismatch')
    lib=ctypes.CDLL(str(dll)); word=ctypes.c_uint32
    fn=lib.scheduler_selected_projection
    fn.argtypes=[word]*6+[ctypes.POINTER(word)]; fn.restype=None
    out=(word*14)()
    def check(index,mode,delay,task):
        callback,argument=0x1333c,0x87654321
        pc,a0,a1,a2,events=verify.run(image,index,callback,mode,delay,argument,task)
        if events[-1]!=('read','gp+166',1): raise ValueError('read event mismatch')
        expected=[pc,a0,a1,a2,*events[0][1:],*events[1][1:],*events[2][1:],1]
        fn(index,callback,mode,delay,argument,task,out)
        if list(out)!=expected: raise ValueError(f'scheduler model mismatch index={index} mode={mode:#x} delay={delay:#x}')
    count=0
    for index in range(15):
        for mode in (0,1,255,256,257,0x10000,0x80000000,0xffffffff):
            for delay in (1,34,35,100,300,0x418937,0x418938,0xffffffff):
                for task in (0,255): check(index,mode,delay,task); count+=1
    for mode in range(65536):
        check(mode%15,mode,0xffffffff if mode&1 else 300,mode&255); count+=1
    print(f'PASS: {count} C model traces including all low-16-bit mode values',flush=True)


def main():
    parser=argparse.ArgumentParser(); group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars',type=Path); group.add_argument('--worker',type=Path); args=parser.parse_args()
    if args.worker: worker(args.worker); return
    with tempfile.TemporaryDirectory(prefix='tsl9-scheduler-mode-') as temp:
        tmp=Path(temp); batch=tmp/'build.bat'
        def compile_one(source,dll,flags):
            batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{source}" /Fe:"{dll}"\n@exit /b %errorlevel%\n',encoding='utf-8')
            subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=tmp,check=True)
        for name,flags in (('C','/TC /std:c11'),('C++','/TP /std:c++17')):
            dll=tmp/(name.replace('+','p')+'.dll'); compile_one(HERE/'model.c',dll,flags)
            print(name+': ',end='',flush=True)
            subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)],check=True)
        text=(HERE/'model.c').read_text(encoding='utf-8')
        mutants=(('narrow_branch','mode == 0','(mode & UINT32_C(0xff)) == 0'),
                 ('wrong_scale','UINT32_C(625)','UINT32_C(624)'),
                 ('slot_stride','index * UINT32_C(12)','index * UINT32_C(16)'),
                 ('byte_write','out[9] = mode & UINT32_C(0xff);','out[9] = mode;'))
        for name,old,new in mutants:
            if text.count(old)!=1: raise ValueError('ambiguous mutant')
            source,dll=tmp/(name+'.c'),tmp/(name+'.dll'); source.write_text(text.replace(old,new),encoding='utf-8')
            compile_one(source,dll,'/TC /std:c11')
            check=subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)],capture_output=True,text=True)
            if check.returncode==0 or 'scheduler model mismatch' not in check.stderr: raise ValueError(f'{name} mutant not rejected')
            print(f'PASS: {name} mutant rejected',flush=True)
    print('Selected-slot assumption only; no scan, provider or physical execution.')

if __name__=='__main__': main()
