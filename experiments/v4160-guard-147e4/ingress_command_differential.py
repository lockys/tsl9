"""Compare C/C++ command-byte event model to pinned APP instruction projection."""
import argparse
import ctypes
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('third',HERE/'ingress_third_byte.py')
third=importlib.util.module_from_spec(spec); spec.loader.exec_module(third)
MASK=0xffffffff

def worker(dll,mutant):
    image=third.prefix.start.gap.clock.gate.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=third.prefix.start.gap.clock.gate.entry.SHA: raise ValueError('firmware identity mismatch')
    code={pc:image[pc-0x8000:pc-0x8000+len(raw)] for pc,raw in third.EXPECTED.items()}
    u=ctypes.c_uint32; fn=ctypes.CDLL(str(dll)).ingress_command_model
    fn.argtypes=[u,u,u,u,ctypes.POINTER(u)]; fn.restype=None
    def compare(gp,s1,command,loaded):
        pc,events=third.run(code,gp,s1,command,loaded)
        want=[pc]
        for event in events: want.extend((event[1],event[3]))
        out=(u*9)(); fn(gp,s1,command,loaded,out)
        return list(out)==want
    if mutant:
        if all(compare(*case) for case in ((0x20004000,0x200040a5,255,2),(MASK,0,131,131))): raise ValueError('semantic mutant not detected')
        print('PASS: semantic mutant rejected',flush=True); return
    count=0
    for command in range(256):
        for loaded in range(256):
            if not compare(0x20004000,0x200040a5,command,loaded): raise ValueError('byte pair mismatch')
            count+=1
    for gp in (0,0xffffff5b,MASK):
        for command in range(256):
            for s1 in (0,(gp+156)&MASK,(gp+164)&MASK,(gp+165)&MASK,MASK):
                for loaded in (0,command,255):
                    if not compare(gp,s1,command,loaded): raise ValueError('boundary/alias mismatch')
                    count+=1
    print(f'PASS: {count} C/original-instruction projection comparisons',flush=True)

def main():
    parser=argparse.ArgumentParser(); group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars',type=Path); group.add_argument('--worker',type=Path)
    parser.add_argument('--mutant',action='store_true'); args=parser.parse_args()
    if args.worker: worker(args.worker,args.mutant); return
    source=(HERE/'ingress_command_model.c').read_text()
    variants=[('base',source),('state',source.replace('out[2] = 3','out[2] = 2')),('command_addr',source.replace('UINT32_C(164)','UINT32_C(163)')),('sum',source.replace('(command + loaded)','(command - loaded)')),('read_addr',source.replace('out[5] = s1','out[5] = gp'))]
    if any(text==source for _,text in variants[1:]): raise ValueError('mutation missing')
    with tempfile.TemporaryDirectory(prefix='tsl9-ingress-command-') as directory:
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
