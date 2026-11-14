"""Compose APP prefix instruction decoder with 0x147e4 C guard.

Reconstruct state at the guard from a stable, successful two-byte read; this
is not continuous execution and does not prove caller reachability or safety.
"""
import argparse
import ctypes
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
prefix=load('prefix',HERE.parent/'v4160-dispatch-148b4-model'/'payload_gate.py')


def worker(dll):
    image=prefix.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=prefix.SHA: raise ValueError('firmware identity mismatch')
    u=ctypes.c_uint32; fn=ctypes.CDLL(str(dll)).guard_147e4; fn.argtypes=[u,u,u,ctypes.POINTER(u)]; fn.restype=None
    count=0; guard_count=0; skipped=0
    def check(length,first,second,base):
        nonlocal count,guard_count,skipped
        pc,reads,trace,regs=prefix.run(image,length,first,second,base)
        count+=1
        if 0x14490 not in trace or 0x14494 not in trace or not reads or reads[0]!=base: raise ValueError('missing predecessor read')
        if length==1:
            if 0x147e4 in trace or pc!=0x14498 or reads!=[base]: raise ValueError('length one bypass mismatch')
            skipped+=1; return
        if 0x147e4 not in trace: raise ValueError('guard not reached in projection')
        out=(u*4)(); fn(first,base,second,out)
        expect_pc=0x147f8 if out[0]==0x147f4 else out[0]
        expect_reads=[base]+([out[2]] if out[1] else [])
        if pc!=expect_pc or reads!=expect_reads: raise ValueError('composed guard mismatch')
        if out[0]==0x147f4 and (regs[10],regs[11])!=(0x1234,2): raise ValueError('post-guard call arguments')
        guard_count+=1
    for first in range(256):
        for second in range(256): check(20,first,second,0x2000b9d8)
    for length in (0,1,2,514,0xffffffff):
        for first in range(256):
            for second in (0,255): check(length,first,second,0xffffffff)
    print(f'PASS: {count} composed cases; {guard_count} reach guard in bounded decoder and {skipped} length-one cases bypass it',flush=True)
    print('Stable synthetic bytes and successful reads assumed; no complete entry or hardware execution.')


def main():
    p=argparse.ArgumentParser(); g=p.add_mutually_exclusive_group(required=True); g.add_argument('--vcvars',type=Path); g.add_argument('--worker',type=Path); args=p.parse_args()
    if args.worker: worker(args.worker); return
    with tempfile.TemporaryDirectory(prefix='tsl9-guard-compose-') as d:
        tmp=Path(d); batch=tmp/'build.bat'
        for label,flags in (('C','/TC /std:c11'),('Cpp','/TP /std:c++17')):
            dll=tmp/(label+'.dll'); batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{HERE / "model.c"}" /Fe:"{dll}"\n@exit /b %errorlevel%\n',encoding='utf8')
            subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=tmp,check=True)
            subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)],check=True)

if __name__=='__main__': main()
