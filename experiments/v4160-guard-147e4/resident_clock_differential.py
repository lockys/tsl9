"""Compare C projection with hash-pinned optional resident candidates.

Return status distinguishes missing carrier from executed tests.
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
spec=importlib.util.spec_from_file_location('candidate',HERE/'resident_clock_candidates.py')
candidate=importlib.util.module_from_spec(spec); spec.loader.exec_module(candidate)
MASK=0xffffffff

def worker(dll,mutant):
    u=ctypes.c_uint32; fn=ctypes.CDLL(str(dll)).resident_clock_model
    fn.argtypes=[u,u,u,u,ctypes.POINTER(u)]; fn.restype=None
    executed=0
    for name,path,digest,entry,callback,counter,hexbytes in candidate.CANDIDATES:
        p=candidate.ROOT/path
        if not p.exists(): print(f'SKIP: {name} carrier missing',flush=True); continue
        raw=p.read_bytes(); expected=bytes.fromhex(hexbytes)
        if hashlib.sha256(raw).hexdigest()!=digest or int.from_bytes(raw[0x7c:0x80],'little')!=entry: raise ValueError('candidate identity mismatch')
        code=raw[entry-0x40000:entry-0x40000+len(expected)]
        if code!=expected: raise ValueError('candidate bytes mismatch')
        def compare(ptr,before,after,delta):
            result,_,_,_,events=candidate.run(code,expected,entry,callback,counter,ptr,before,after,delta,0x20001000,0x8908,0x12345678)
            calls=[e for e in events if e[0]=='call']; writes=[e for e in events if e[0]=='write' and e[1]==counter]
            want=[len(calls),calls[0][1] if calls else 0,len(writes),result]
            out=(u*4)(); fn(ptr,before,after,delta,out)
            return list(out)==want
        if mutant:
            if all(compare(*case) for case in ((0,1,2,3),(1,0,1,2),(0x1235,1,MASK,2))): raise ValueError('mutant undetected')
            print(f'PASS: {name} semantic mutant rejected',flush=True)
        else:
            count=0
            for i in range(65536):
                for ptr in (0,1,0x1234,0x1235):
                    if not compare(ptr,i,(i*65537)&MASK,(MASK-i)&MASK): raise ValueError('differential mismatch')
                    count+=1
            print(f'PASS: {name} {count} C/candidate comparisons',flush=True)
        executed+=1
    if not executed: raise ValueError('no optional candidates available; comparisons not run')

def main():
    parser=argparse.ArgumentParser(); group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars',type=Path); group.add_argument('--worker',type=Path)
    parser.add_argument('--mutant',action='store_true'); args=parser.parse_args()
    if args.worker: worker(args.worker,args.mutant); return
    source=(HERE/'resident_clock_model.c').read_text()
    variants=[('base',source),('condition',source.replace('pointer != 0','pointer == 0')),('counter',source.replace('callback_after + callback_delta','before + callback_delta')),('target',source.replace('pointer & ~UINT32_C(1)','pointer'))]
    if any(text==source for _,text in variants[1:]): raise ValueError('mutation missing')
    with tempfile.TemporaryDirectory(prefix='tsl9-resident-clock-') as directory:
        tmp=Path(directory)
        for language,flags in (('C','/TC /std:c11'),('Cpp','/TP /std:c++17')):
            for name,text in variants:
                src=tmp/(language+name+'.c'); dll=tmp/(language+name+'.dll'); batch=tmp/'build.bat'; src.write_text(text)
                batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{src}" /Fe:"{dll}"\n@exit /b %errorlevel%\n')
                subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=tmp,check=True)
                cmd=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)]
                if name!='base': cmd.append('--mutant')
                subprocess.run(cmd,check=True)
if __name__=='__main__': main()
