"""Compare C state routing against bounded original-byte decoding."""
import argparse
import ctypes
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('route',HERE/'ingress_length_route.py')
route=importlib.util.module_from_spec(spec); spec.loader.exec_module(route)

def worker(dll,mutant):
    image=route.gate.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=route.gate.entry.SHA: raise ValueError('firmware identity mismatch')
    code=image[0x89da-0x8000:0x89f6-0x8000]
    if code!=route.EXPECTED: raise ValueError('original bytes mismatch')
    u=ctypes.c_uint32; fn=ctypes.CDLL(str(dll)).ingress_length_route_model
    fn.argtypes=[u,u,ctypes.POINTER(u)]; fn.restype=None
    def compare(gp,length):
        events,_,_=route.run(code,gp,length)
        out=(u*3)(); fn(gp,length,out)
        return list(out)==[0x89a8,events[0][0],events[0][2]] and len(events)==1 and events[0][1]==1
    if mutant:
        if all(compare(*case) for case in ((0x20004000,0),(0x20004000,1040),(0xffffffff,0x10000))): raise ValueError('semantic mutant not detected')
        print('PASS: semantic mutant rejected',flush=True); return
    count=0
    for value in range(65536):
        if not compare(0x20004000,value): raise ValueError('halfword mismatch')
        count+=1
    for gp in (0,0xffffff64,0xffffffff):
        for value in (0,1,1039,1040,1041,65535,65536,0x80000000,0xffffffff):
            if not compare(gp,value): raise ValueError('boundary mismatch')
            count+=1
    print(f'PASS: {count} C/original-byte decoder comparisons',flush=True)

def main():
    parser=argparse.ArgumentParser(); group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars',type=Path); group.add_argument('--worker',type=Path)
    parser.add_argument('--mutant',action='store_true'); args=parser.parse_args()
    if args.worker: worker(args.worker,args.mutant); return
    source=(HERE/'ingress_length_route_model.c').read_text()
    variants=[('base',source),('zero',source.replace('length == 0 ? 6u','length == 0 ? 5u')),
              ('boundary',source.replace('length <= UINT32_C(1040)','length < UINT32_C(1040)')),
              ('truncation',source.replace('length == 0 ? 6u','(length & UINT32_C(65535)) == 0 ? 6u')),
              ('address',source.replace('gp + UINT32_C(156)','gp + UINT32_C(155)'))]
    if any(text==source for _,text in variants[1:]): raise ValueError('mutation did not apply')
    with tempfile.TemporaryDirectory(prefix='tsl9-length-route-') as directory:
        tmp=Path(directory)
        for label,flags in (('C','/TC /std:c11'),('Cpp','/TP /std:c++17')):
            for name,text in variants:
                src=tmp/(label+name+'.c'); dll=tmp/(label+name+'.dll'); batch=tmp/'build.bat'; src.write_text(text)
                batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{src}" /Fe:"{dll}"\n@exit /b %errorlevel%\n')
                subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=tmp,check=True)
                command=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)]
                if name!='base': command.append('--mutant')
                subprocess.run(command,check=True)

if __name__=='__main__': main()
