"""C event projection against two pinned APP instruction projections."""
import argparse
import ctypes
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('second',HERE/'ingress_second_byte.py')
second=importlib.util.module_from_spec(spec); spec.loader.exec_module(second)
MASK=0xffffffff

def worker(dll,mutant):
    image=second.start.gap.clock.gate.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=second.start.gap.clock.gate.entry.SHA: raise ValueError('firmware identity mismatch')
    read=lambda mapping:{pc:image[pc-0x8000:pc-0x8000+len(raw)] for pc,raw in mapping.items()}
    first=read(second.start.EXPECTED); second_code=read(second.EXPECTED)
    u=ctypes.c_uint32; fn=ctypes.CDLL(str(dll)).ingress_prefix_model
    fn.argtypes=[u,u,u,ctypes.POINTER(u)]; fn.restype=None
    def compare(gp,a,b):
        pc,events=second.start.first(first,gp,a)
        if pc==0x897e:
            pc,events2=second.run(second_code,gp,b,events[0][3]); events+=events2
        want=[pc,len(events),0,0,0,0,0,0]
        for i,event in enumerate(events): want[2+2*i:4+2*i]=[event[1],event[3]]
        out=(u*8)(); fn(gp,a,b,out)
        return list(out)==want
    if mutant:
        if all(compare(*case) for case in ((0x20004000,0x54,0x7f),(0x20004000,0x55,0x7e),(0x20004000,0x55,0x7f))): raise ValueError('semantic mutant not detected')
        print('PASS: semantic mutant rejected',flush=True); return
    count=0
    for a in range(256):
        for b in range(256):
            if not compare(0x20004000,a,b): raise ValueError('byte pair mismatch')
            count+=1
    for gp in (0,0xffffff5b,MASK):
        for a in range(256):
            for b in (0,0x7e,0x7f,0x80,255):
                if not compare(gp,a,b): raise ValueError('address boundary mismatch')
                count+=1
    print(f'PASS: {count} C/original-instruction projection comparisons',flush=True)

def main():
    parser=argparse.ArgumentParser(); group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars',type=Path); group.add_argument('--worker',type=Path)
    parser.add_argument('--mutant',action='store_true'); args=parser.parse_args()
    if args.worker: worker(args.worker,args.mutant); return
    source=(HERE/'ingress_prefix_model.c').read_text()
    variants=[('base',source),('first',source.replace('0x55','0x54')),('second',source.replace('0x7f','0x7e')),('state',source.replace('out[5] = 2','out[5] = 3')),('checksum',source.replace('UINT32_C(165)','UINT32_C(164)'))]
    if any(text==source for _,text in variants[1:]): raise ValueError('mutation missing')
    with tempfile.TemporaryDirectory(prefix='tsl9-prefix-') as directory:
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
