"""Compare C/C++ callee projection with the bounded original instruction table."""
import argparse
import ctypes
import hashlib
import importlib.util
import itertools
from pathlib import Path
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('event_callee',HERE/'callee.py')
callee=importlib.util.module_from_spec(spec); spec.loader.exec_module(callee)


def worker(dll):
    image=callee.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=callee.SHA: raise ValueError('firmware identity mismatch')
    lib=ctypes.CDLL(str(dll)); word=ctypes.c_uint32
    fn=lib.event_callee_projection
    fn.argtypes=[word]*8+[ctypes.POINTER(word)]; fn.restype=None
    out=(word*19)()
    def check(values, ret):
        sp,ra=0x20001000,0x12345678
        result,actual_sp,actual_ra,events=callee.run(image,values,sp,ra,ret)
        reads=[e[1] for e in events if e[0]=='read']
        writes=[e for e in events if e[0]=='write']; calls=[e for e in events if e[0]=='call']
        if writes and events[-2:] != (writes[0],calls[0]): raise ValueError('event ordering mismatch')
        want=[result,actual_sp,actual_ra,len(reads),*reads,*([0]*(6-len(reads))),
              len(writes),writes[0][1] if writes else 0,writes[0][3] if writes else 0,
              len(calls),*(list(calls[0][1:]) if calls else [0]*5)]
        fn(*values,sp,ra,out)
        if list(out)!=want: raise ValueError(f'callee model mismatch {values}')
    count=0
    for values in itertools.product((0xfffe,0x1234),(0,1,2,255),(0,1,2,255),(0xfffe,0x1234),(0,1,2,255),(0,1,2,255)):
        for ret in (0,0xffffffff): check(values,ret); count+=1
    for value in range(65536):
        for values in ((value,1,1,0xfffe,0,0),(0xfffe,0,0,value,1,1)):
            check(values,0xffffffff); count+=1
    print(f'PASS: {count} synthetic model comparisons, including each halfword value',flush=True)


def main():
    parser=argparse.ArgumentParser(); group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars',type=Path); group.add_argument('--worker',type=Path); args=parser.parse_args()
    if args.worker: worker(args.worker); return
    with tempfile.TemporaryDirectory(prefix='tsl9-event-callee-') as temp:
        tmp=Path(temp); batch=tmp/'build.bat'
        def compile_one(source,dll,flags):
            batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{source}" /Fe:"{dll}"\n@exit /b %errorlevel%\n',encoding='utf-8')
            subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=tmp,check=True)
        for name,flags in (('C','/TC /std:c11'),('C++','/TP /std:c++17')):
            dll=tmp/(name.replace('+','p')+'.dll'); compile_one(HERE/'callee_model.c',dll,flags)
            print(name+': ',end='',flush=True)
            subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)],check=True)
        text=(HERE/'callee_model.c').read_text(encoding='utf-8')
        mutants=(('first_sentinel','h0 != UINT32_C(0xfffe)','h0 == UINT32_C(0xfffe)'),
                 ('second_sentinel','h1 != UINT32_C(0xfffe)','h1 == UINT32_C(0xfffe)'),
                 ('first_activity','selected = a0 != 0;','selected = a0 == 0;'),
                 ('flag','out[12] = 1;','out[12] = 2;'))
        for name,old,new in mutants:
            if text.count(old)!=1: raise ValueError('ambiguous mutant')
            source,dll=tmp/(name+'.c'),tmp/(name+'.dll'); source.write_text(text.replace(old,new),encoding='utf-8')
            compile_one(source,dll,'/TC /std:c11')
            check=subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)],capture_output=True,text=True)
            if check.returncode==0 or 'callee model mismatch' not in check.stderr: raise ValueError(f'{name} mutant not rejected')
            print(f'PASS: {name} mutant rejected',flush=True)
    print('Returning scheduler stub; no physical accesses, scheduler effects, or hardware.')

if __name__=='__main__': main()
