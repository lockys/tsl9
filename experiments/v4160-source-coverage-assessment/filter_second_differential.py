"""C projection vs fixed original-instruction projection for 0x12920."""
import argparse
import ctypes
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('oracle',HERE/'filter_second_call_12920.py')
oracle=importlib.util.module_from_spec(spec); spec.loader.exec_module(oracle)


def worker(dll,mutant):
    image=oracle.entry.calls.case.dispatch.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=oracle.entry.calls.case.dispatch.SHA: raise ValueError('APP identity mismatch')
    u=ctypes.c_uint32; fn=ctypes.CDLL(str(dll)).tsl9_filter_second
    fn.argtypes=[u,u,u,u,ctypes.POINTER(u)]; fn.restype=None
    def check(sp,s0,s1,provider):
        want=oracle.project(image,sp,s0,s1,provider)
        out=(u*5)(); fn(sp,s0,s1,provider,out)
        return tuple(out)==want
    if mutant:
        cases=((0,0,1,3),(0xffffffff,113,7,0xffffffff),(0,0x100,7,3),(0,112,7,3))
        if all(check(*case) for case in cases): raise ValueError('mutant accepted')
        print('PASS: mutant rejected',flush=True); return
    for s0 in range(65536):
        for sp,provider in ((0,1),(0xfffffff0,0xffffffff)):
            if not check(sp,s0,0xdeadbeef,provider): raise ValueError('comparison failed')
    for s0 in (0,1,111,112,113,255,256,0xffffffff):
        for sp in (0,0xffffffff):
            for s1 in (0,0xffffffff):
                for provider in (0,1,0xffffffff):
                    if not check(sp,s0,s1,provider): raise ValueError('boundary mismatch')
    print('PASS: 131072 comparisons and 96 full-width boundaries',flush=True)


def main():
    p=argparse.ArgumentParser(); group=p.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars',type=Path); group.add_argument('--worker',type=Path); p.add_argument('--mutant',action='store_true'); args=p.parse_args()
    if args.worker: worker(args.worker,args.mutant); return
    source=(HERE/'filter_second_model.c').read_text(encoding='utf-8'); variants=[('base',source)]
    for name,old,new in (('cap','112u ? 112u','111u ? 111u'),('width','s0>112u','(s0 & 255u)>112u'),('target','0xfffffffe','0xffffffff'),('sp','UINT32_C(32)','UINT32_C(36)')):
        if source.count(old)!=1: raise ValueError('ambiguous mutant')
        variants.append((name,source.replace(old,new)))
    with tempfile.TemporaryDirectory(prefix='tsl9-filter-') as temp:
        folder=Path(temp)
        for label,flags in (('C','/TC /std:c11'),('Cpp','/TP /std:c++17')):
            for name,text in variants:
                src=folder/(label+name+'.c'); dll=folder/(label+name+'.dll'); batch=folder/'build.bat'; src.write_text(text,encoding='utf-8')
                batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{src}" /Fe:"{dll}"\n@exit /b %errorlevel%\n',encoding='utf-8')
                subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=folder,check=True)
                cmd=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)]
                if name!='base': cmd.append('--mutant')
                subprocess.run(cmd,check=True)
    print('Post-first-provider live state assumed; providers and hardware not executed.')

if __name__=='__main__': main()
