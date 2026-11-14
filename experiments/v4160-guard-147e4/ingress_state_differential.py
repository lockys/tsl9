"""Compare the C state gate to bounded decoding of original instructions."""
import argparse
import ctypes
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('gate',HERE/'ingress_state_gate.py')
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

def worker(dll,mutant):
    image=gate.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=gate.entry.SHA: raise ValueError('firmware identity mismatch')
    code=image[0x89f6-0x8000:0x8a06-0x8000]
    if code!=gate.EXPECTED: raise ValueError('original bytes mismatch')
    u=ctypes.c_uint32
    fn=ctypes.CDLL(str(dll)).ingress_state_model
    fn.argtypes=[u,u,u,u,u,ctypes.POINTER(u)]; fn.restype=None
    def compare(gp,a4,s9,halfword,initial_a2=0):
        pc,reads,a2,out_a4,_=gate.run(code,gp,a4,s9,halfword,initial_a2)
        expected=[pc,len(reads),reads[0] if reads else 0,a2,out_a4]
        out=(u*5)(); fn(gp,a4,s9,halfword,initial_a2,out)
        return list(out)==expected
    if mutant:
        cases=((0,1,0,0),(0xffffffff,5,5,1039),(0,5,5,0x8000))
        if all(compare(*case) for case in cases): raise ValueError('semantic mutant not detected')
        print('PASS: semantic mutant rejected',flush=True)
        return
    count=0
    for halfword in range(65536):
        for a4,s9 in ((5,5),(5,6)):
            if not compare(0x20004000,a4,s9,halfword): raise ValueError('halfword mismatch')
            count+=1
    for gp in (0,0xffffff76,0xffffffff):
        for a4,s9 in ((0,0),(0,1),(0xffffffff,0),(0xffffffff,0xffffffff)):
            for halfword in (0,1,1038,1039,1040,32767,32768,65535):
                if not compare(gp,a4,s9,halfword): raise ValueError('boundary mismatch')
                count+=1
    for initial_a2 in (0,1,0x10000,0x80000000,0xffffffff):
        for a4,s9 in ((5,5),(5,6)):
            if not compare(0x20004000,a4,s9,1039,initial_a2): raise ValueError('initial a2 mismatch')
            count+=1
    print(f'PASS: {count} C/original-decoder comparisons',flush=True)

def main():
    parser=argparse.ArgumentParser(); group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars',type=Path); group.add_argument('--worker',type=Path)
    parser.add_argument('--mutant',action='store_true'); args=parser.parse_args()
    if args.worker:
        worker(args.worker,args.mutant); return
    source=(HERE/'ingress_state_model.c').read_text()
    variants=[('base',source),('state',source.replace('a4 != s9','a4 == s9')),
              ('threshold',source.replace('out[3] > UINT32_C(1039)','out[3] >= UINT32_C(1039)')),
              ('signed',source.replace('out[3] > UINT32_C(1039)','(out[3] & UINT32_C(0x8000)) == 0 && out[3] > UINT32_C(1039)')),
              ('address',source.replace('gp + UINT32_C(138)','gp + UINT32_C(139)'))]
    if any(text==source for _,text in variants[1:]): raise ValueError('mutation did not apply')
    with tempfile.TemporaryDirectory(prefix='tsl9-state-') as directory:
        tmp=Path(directory)
        for label,flags in (('C','/TC /std:c11'),('Cpp','/TP /std:c++17')):
            for name,text in variants:
                src=tmp/(label+name+'.c'); dll=tmp/(label+name+'.dll'); batch=tmp/'build.bat'
                src.write_text(text)
                batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{src}" /Fe:"{dll}"\n@exit /b %errorlevel%\n')
                subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=tmp,check=True)
                command=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)]
                if name!='base': command.append('--mutant')
                subprocess.run(command,check=True)

if __name__=='__main__': main()
