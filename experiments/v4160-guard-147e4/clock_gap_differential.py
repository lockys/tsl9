"""Compare C/C++ event projection against the fixed original-byte interpreter."""
import argparse
import ctypes
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('gap',HERE/'clock_gap_composition.py')
gap=importlib.util.module_from_spec(spec); spec.loader.exec_module(gap)
MASK=0xffffffff

def worker(dll,mutant):
    image=gap.clock.gate.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=gap.clock.gate.entry.SHA: raise ValueError('firmware identity mismatch')
    code={pc:image[pc-0x8000:pc-0x8000+len(raw)] for pc,raw in gap.EXPECTED.items()}
    u=ctypes.c_uint32
    fn=ctypes.CDLL(str(dll)).clock_gap_model
    fn.argtypes=[u,u,u,ctypes.POINTER(u)]; fn.restype=None
    def compare(gp,now,prior):
        events=gap.run(code,gp,now,prior); clear=len(events)==3
        expected=[events[0][1],int(clear),events[1][1] if clear else 0,events[-1][1],events[-1][3]]
        out=(u*5)(); fn(gp,now,prior,out)
        return list(out)==expected
    if mutant:
        cases=((0x20004000,299,0),(0x20004000,300,0),(MASK,0,1))
        if all(compare(*case) for case in cases): raise ValueError('semantic mutant not detected')
        print('PASS: semantic mutant rejected',flush=True); return
    count=0
    for prior in range(65536):
        for delta in (0,1,298,299,300,301,MASK):
            if not compare(0x20004000,(prior+delta)&MASK,prior): raise ValueError('comparison mismatch')
            count+=1
    for gp in (0,0xffffff5f,0xffffffff):
        for now in (0,1,299,300,MASK):
            for prior in (0,1,299,300,MASK):
                if not compare(gp,now,prior): raise ValueError('boundary mismatch')
                count+=1
    print(f'PASS: {count} C/original-projection comparisons',flush=True)

def main():
    parser=argparse.ArgumentParser(); g=parser.add_mutually_exclusive_group(required=True)
    g.add_argument('--vcvars',type=Path); g.add_argument('--worker',type=Path)
    parser.add_argument('--mutant',action='store_true'); args=parser.parse_args()
    if args.worker: worker(args.worker,args.mutant); return
    source=(HERE/'clock_gap_model.c').read_text()
    variants=[('base',source),('threshold',source.replace('> UINT32_C(299)','>= UINT32_C(299)')),('direction',source.replace('now - prior','prior - now')),('clear_addr',source.replace('gp + UINT32_C(156)','gp + UINT32_C(155)'))]
    if any(text==source for _,text in variants[1:]): raise ValueError('mutation missing')
    with tempfile.TemporaryDirectory(prefix='tsl9-clock-gap-') as directory:
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
