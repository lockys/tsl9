"""Compare C event projection with original-byte shared-memory decoder."""
import argparse
import ctypes
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('init',HERE/'ingress_length_initialize.py')
init=importlib.util.module_from_spec(spec); spec.loader.exec_module(init)
MASK=0xffffffff

def worker(dll,mutant):
    image=init.gate.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=init.gate.entry.SHA: raise ValueError('firmware identity mismatch')
    code=image[0x89cc-0x8000:0x89da-0x8000]
    if code!=init.EXPECTED: raise ValueError('original bytes mismatch')
    u=ctypes.c_uint32; fn=ctypes.CDLL(str(dll)).ingress_length_initialize_model
    fn.argtypes=[u,u,u,u,ctypes.POINTER(u)]; fn.restype=None
    def compare(gp,s11,a5,memory):
        value,events=init.run(code,gp,s11,a5,dict(memory))
        if len(events)!=3 or [x[0] for x in events]!=['write','read','write']: raise ValueError('decoder event order mismatch')
        loaded=events[1][3]
        out=(u*10)(); fn(gp,s11,a5,loaded,out)
        expected=[value,*events[0][1:],*events[1][1:],*events[2][1:]]
        return list(out)==expected
    if mutant:
        memory={}; init.put(memory,0x1000,2,0x8001)
        if all(compare(*case) for case in ((0x20004000,0x1000,0x10000,memory),(0xffffffff,0x1000,1,memory))): raise ValueError('semantic mutant not detected')
        print('PASS: semantic mutant rejected',flush=True); return
    count=0
    for loaded in range(65536):
        for a5 in (0,0x10000):
            memory={}; init.put(memory,0x1000,2,loaded)
            if not compare(0x20004000,0x1000,a5,memory): raise ValueError('value mismatch')
            count+=1
    for gp in (0,0xffffff76,MASK):
        for delta in (-1,0,1,2,3,4,5):
            for a5 in (0,0x10000,MASK):
                address=(gp+138)&MASK; memory={}
                for i in range(-1,7): memory[(address+i)&MASK]=(i*37+113)&255
                if not compare(gp,(address+delta)&MASK,a5,memory): raise ValueError('alias mismatch')
                count+=1
    memory={}; init.put(memory,0x2000408a,2,0xffff)
    value,events=init.run(code,0x20004000,0x2000408a,0,memory)
    if value!=0 or events[1][3]!=0: raise ValueError('write-before-read witness missing')
    print(f'PASS: {count} C/original-byte decoder comparisons, including alias/wrap cases',flush=True)
    print('PASS: overlapping counter is read after its clearing write',flush=True)

def main():
    parser=argparse.ArgumentParser(); group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars',type=Path); group.add_argument('--worker',type=Path)
    parser.add_argument('--mutant',action='store_true'); args=parser.parse_args()
    if args.worker: worker(args.worker,args.mutant); return
    source=(HERE/'ingress_length_initialize_model.c').read_text()
    variants=[('base',source),('and',source.replace(') | a5',') & a5')),
              ('counter',source.replace('gp + UINT32_C(138)','gp + UINT32_C(139)')),
              ('length',source.replace('gp + UINT32_C(142)','gp + UINT32_C(141)')),
              ('truncate',source.replace(') | a5',') | (a5 & UINT32_C(65535))'))]
    if any(text==source for _,text in variants[1:]): raise ValueError('mutation did not apply')
    with tempfile.TemporaryDirectory(prefix='tsl9-length-init-') as directory:
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
