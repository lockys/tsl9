"""Compare C data-selected delay projection to bounded original instruction run."""
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
spec=importlib.util.spec_from_file_location('caller',HERE/'data_delay_caller.py'); caller=importlib.util.module_from_spec(spec); spec.loader.exec_module(caller)


def worker(dll):
    image=caller.v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=caller.v.SHA: raise ValueError('firmware identity mismatch')
    lib=ctypes.CDLL(str(dll)); word=ctypes.c_uint32; fn=lib.scheduler_data_delay
    fn.argtypes=[word]*6+[ctypes.POINTER(word)]; fn.restype=None
    out=(word*17)(); rng=random.Random(416009)
    for n in range(65536):
        byte=n&255; clock=rng.getrandbits(32); gp=rng.getrandbits(30)*4; pointer=rng.getrandbits(30)*4; sp=(0xfffffff0 if n&1 else rng.getrandbits(30)*4); ra=rng.getrandbits(32)
        args,end,ret,events=caller.run(image,byte,clock,gp,pointer,sp,ra)
        # This projection assumes all supplied synthetic reads are independent
        # even if numeric addresses overlap: it does not model physical RAM.
        if events[4][0]!='write' or events[5]!=('call',0x81b0) or events[6][0]!='read' or events[7][0]!='read' or events[8][0]!='write': raise ValueError('original event mismatch')
        expected=[*args,end,ret,events[0][1],events[0][3],events[1][1],events[1][3],events[2][1],events[2][3],events[3][1],events[3][3],events[4][1],events[8][1],events[8][3]]
        fn(byte,clock,gp,pointer,sp,ra,out)
        if list(out)!=expected: raise ValueError(f'data delay model mismatch case={n}, byte={byte}')
    print('PASS: 65536 C projections including all byte values and synthetic pointer/clock wrap',flush=True)


def main():
    parser=argparse.ArgumentParser(); group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars',type=Path); group.add_argument('--worker',type=Path); args=parser.parse_args()
    if args.worker: worker(args.worker); return
    with tempfile.TemporaryDirectory(prefix='tsl9-data-delay-') as temp:
        tmp=Path(temp); batch=tmp/'build.bat'
        def build(source,dll,flags):
            batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{source}" /Fe:"{dll}"\n@exit /b %errorlevel%\n',encoding='utf-8')
            subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=tmp,check=True)
        for label,flags in (('C','/TC /std:c11'),('C++','/TP /std:c++17')):
            dll=tmp/(label.replace('+','p')+'.dll'); build(HERE/'data_delay_model.c',dll,flags)
            print(label+': ',end='',flush=True)
            subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)],check=True)
        text=(HERE/'data_delay_model.c').read_text(encoding='utf-8')
        for name,old,new in (('selector','data_byte >> 6','data_byte >> 7'),('table','{0,1,5,10}','{0,1,4,10}'),('unit','UINT32_C(60000)','UINT32_C(6000)'),('destination','UINT32_C(0x2000bef0)','UINT32_C(0x2000bef4)')):
            if text.count(old)!=1: raise ValueError('ambiguous mutant')
            source,dll=tmp/(name+'.c'),tmp/(name+'.dll'); source.write_text(text.replace(old,new),encoding='utf-8'); build(source,dll,'/TC /std:c11')
            proc=subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)],capture_output=True,text=True)
            if proc.returncode==0 or 'data delay model mismatch' not in proc.stderr: raise ValueError(f'mutant not rejected: {name}')
            print(f'PASS: {name} mutant rejected',flush=True)
    print('Prior call results and independent successful reads assumed; no provider or hardware execution.')

if __name__=='__main__': main()
