"""Compare C projection with the bounded original-instruction decoder."""
import argparse
import ctypes
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('gate', HERE / 'ingress_checksum_gate.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

def worker(dll, mutant):
    image = gate.entry.IMAGE.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != gate.entry.SHA:
        raise ValueError('firmware identity mismatch')
    code = image[0x8a2a-0x8000:0x8a36-0x8000]
    if code != gate.EXPECTED: raise ValueError('original bytes mismatch')
    u = ctypes.c_uint32
    fn = ctypes.CDLL(str(dll)).ingress_checksum_model
    fn.argtypes = [u,u,u,u,u,ctypes.POINTER(u)]
    fn.restype = None
    def compare(gp,a4,s10,a5,loaded):
        pc, reads, _ = gate.run(code,gp,a4,s10,a5,loaded)
        expected = [pc,len(reads),reads[0] if reads else 0]
        out = (u*3)()
        fn(gp,a4,s10,a5,loaded,out)
        return list(out) == expected
    if mutant:
        cases = ((0x20004000,0,1,0,0),(0xffffffff,1,1,0x100,0),(0,1,1,1,1))
        if all(compare(*args) for args in cases): raise ValueError('semantic mutant not detected')
        print('PASS: semantic mutant rejected',flush=True)
        return
    count = 0
    for loaded in range(256):
        for a5 in range(256):
            if not compare(0x20004000,7,7,a5,loaded): raise ValueError('byte pair mismatch')
            count += 1
    for gp in (0,0xffffff5b,0xffffffff):
        for a4,s10 in ((0,0),(0,1),(0xffffffff,0xffffffff),(0xffffffff,0)):
            for loaded in range(256):
                for a5 in (loaded,loaded | 0x100,0xffffffff):
                    if not compare(gp,a4,s10,a5,loaded): raise ValueError('boundary mismatch')
                    count += 1
    print(f'PASS: {count} original-decoder comparisons including full byte pairs and 32-bit boundaries',flush=True)

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars',type=Path)
    group.add_argument('--worker',type=Path)
    parser.add_argument('--mutant',action='store_true')
    args = parser.parse_args()
    if args.worker:
        worker(args.worker,args.mutant)
        return
    source = (HERE/'ingress_checksum_model.c').read_text()
    variants = [('base',source),('first',source.replace('a4 != s10','a4 == s10')),
                ('truncate',source.replace('a5 == (loaded & UINT32_C(255))','(a5 & UINT32_C(255)) == (loaded & UINT32_C(255))')),
                ('read-address',source.replace('gp + UINT32_C(165)','gp + UINT32_C(164)'))]
    if any(text == source for _,text in variants[1:]): raise ValueError('mutation did not apply')
    with tempfile.TemporaryDirectory(prefix='tsl9-checksum-') as directory:
        tmp = Path(directory)
        for language,flags in (('C','/TC /std:c11'),('Cpp','/TP /std:c++17')):
            for name,text in variants:
                src=tmp/(language+name+'.c'); dll=tmp/(language+name+'.dll'); batch=tmp/'build.bat'
                src.write_text(text)
                batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{src}" /Fe:"{dll}"\n@exit /b %errorlevel%\n')
                subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=tmp,check=True)
                command=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)]
                if name != 'base': command.append('--mutant')
                subprocess.run(command,check=True)

if __name__ == '__main__': main()
