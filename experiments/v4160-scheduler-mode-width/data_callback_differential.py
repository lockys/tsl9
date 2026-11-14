"""Differential checks between C projection and fixed original instructions."""
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
spec=importlib.util.spec_from_file_location('callback',HERE/'data_delay_callback.py'); callback=importlib.util.module_from_spec(spec); spec.loader.exec_module(callback)


def worker(dll):
    image=callback.v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=callback.v.SHA: raise ValueError('firmware identity mismatch')
    word=ctypes.c_uint32; fn=ctypes.CDLL(str(dll)).scheduler_data_callback
    fn.argtypes=[word]*6+[ctypes.POINTER(word)]; fn.restype=None
    rng=random.Random(4160254)
    for n in range(65536):
        byte=n&255; value=(0 if (n>>8)&1 else rng.getrandbits(32)|1)
        gp=rng.getrandbits(32); pointer=rng.getrandbits(32); sp=rng.getrandbits(32); ra=rng.getrandbits(32)
        kind,pc,a0,end,ret,events=callback.run(image,byte,value,gp,pointer,sp,ra)
        out=(word*34)(); fn(byte,value,gp,pointer,sp,ra,out)
        encoded=[]
        for ev in events:
            if ev[0]=='call': encoded.extend((3,ev[1],0,ev[2]))
            else: encoded.extend((1 if ev[0]=='read' else 2,ev[1],ev[2],ev[3]))
        expected=[1 if kind=='tail' else 0,pc,a0 or 0,end,ret]+encoded
        if list(out[:len(expected)])!=expected or out[33]!=len(events): raise ValueError(f'callback model mismatch case {n}')
    print('PASS: 65536 callback C projections; all byte values, zero/nonzero words and address wrap',flush=True)


def main():
    parser=argparse.ArgumentParser(); group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars',type=Path); group.add_argument('--worker',type=Path); args=parser.parse_args()
    if args.worker: worker(args.worker); return
    with tempfile.TemporaryDirectory(prefix='tsl9-callback-') as temp:
        tmp=Path(temp); batch=tmp/'build.bat'
        def build(source,dll,flags):
            batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{source}" /Fe:"{dll}"\n@exit /b %errorlevel%\n',encoding='utf-8')
            subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=tmp,check=True)
        source=HERE/'data_callback_model.c'
        for label,flags in (('C','/TC /std:c11'),('C++','/TP /std:c++17')):
            dll=tmp/(label.replace('+','p')+'.dll'); build(source,dll,flags)
            print(label+': ',end='',flush=True)
            subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)],check=True)
        text=source.read_text(encoding='utf-8')
        for name,old,new in (('mask','byte & 192u','byte & 128u'),('gate','word != 0','word == 0'),('tail','UINT32_C(0xb29a)','UINT32_C(0xb298)'),('stack','sp - 4u','sp - 8u')):
            if text.count(old)<1: raise ValueError('mutant absent')
            altered=tmp/(name+'.c'); dll=tmp/(name+'.dll'); altered.write_text(text.replace(old,new),encoding='utf-8'); build(altered,dll,'/TC /std:c11')
            p=subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)],capture_output=True,text=True)
            if p.returncode==0 or 'callback model mismatch' not in p.stderr: raise ValueError(f'mutant not rejected: {name}')
            print(f'PASS: {name} mutant rejected',flush=True)
    print('Independent synthetic reads; 0x90b0 is a returning stub; no hardware execution.')

if __name__=='__main__': main()
