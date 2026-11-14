"""C/C++ event projection versus two original-byte instruction decoders.

The supplied length is the successful post-store read value. Independent
inputs are synthetic; no actual provider, target execution or C ABI claim.
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
    spec=importlib.util.spec_from_file_location(name,path); obj=importlib.util.module_from_spec(spec); spec.loader.exec_module(obj); return obj
store=load('store',HERE/'ingress_payload_store.py'); transition=load('transition',HERE/'ingress_payload_transition.py'); alias=load('alias',HERE/'ingress_store_length_alias.py')
MASK=0xffffffff

def worker(dll,mutant):
    image=store.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=store.entry.SHA: raise ValueError('firmware identity mismatch')
    a=image[0x8a02-0x8000:0x8a20-0x8000]; b=image[0x8a20-0x8000:0x8a2a-0x8000]
    if a!=store.EXPECTED or b!=transition.EXPECTED: raise ValueError('original bytes mismatch')
    u=ctypes.c_uint32; fn=ctypes.CDLL(str(dll)).ingress_store_model; fn.argtypes=[u,u,u,u,ctypes.POINTER(u)]; fn.restype=None
    def compare(gp,index,byte,length):
        pc,writes,_=store.run(a,gp,index,byte)
        if pc==0x8a4c: expected=[pc,0,0,0,0,0,0,0,0]
        else:
            pc,reads,_=transition.run(b,gp,index+1,length)
            expected=[pc,2,*writes[0],*writes[1],reads[0]]
        out=(u*9)(); fn(gp,index,byte,length,out)
        return list(out)==expected
    if mutant:
        if all(compare(*case) for case in ((0x20004000,1039,0x1ab,1040),(0xffffffff,2,0x1ab,3),(0,1040,0,0))): raise ValueError('semantic mutant not detected')
        print('PASS: semantic mutant rejected'); return
    count=0
    for index in range(65536):
        for length in (0,1040,65535):
            if not compare(0x20004000,index,0x123,length): raise ValueError(f'index mismatch {index:#x} length {length:#x}')
            count+=1
    for gp in (0,0xffffff76,0xffffffff):
        for index in (0,1,1039,1040,65535,0xffffffff):
            for byte in (0,1,255,256,0xffffffff):
                for length in (0,1,1040,65535):
                    if not compare(gp,index,byte,length): raise ValueError('boundary mismatch')
                    count+=1
    for byte in range(256):
        for gp in (0x2000b94a,0x20004000):
            loaded,pc,writes=alias.run(image,gp,0,2,byte)
            expected_length=byte if gp==0x2000b94a else 2
            if loaded!=expected_length or pc!=(0x89a8 if loaded>1 else 0x89dc): raise ValueError('shared-memory projection mismatch')
            if not compare(gp,0,byte,loaded): raise ValueError('C alias comparison mismatch')
            count+=1
    actual_length,actual_pc,_=alias.run(image,0x2000b94a,0,2,0)
    stale=(u*9)(); fn(0x2000b94a,0,0,2,stale)
    if (actual_length,actual_pc,stale[0])!=(0,0x89dc,0x89a8): raise ValueError('stale-length counterexample missing')
    print(f'PASS: {count} C/original-decoder comparisons including 512 shared-memory alias/control cases',flush=True)
    print('PASS: stale pre-write length changes the predicted branch in the synthetic overlap witness',flush=True)


def main():
    parser=argparse.ArgumentParser(); group=parser.add_mutually_exclusive_group(required=True); group.add_argument('--vcvars',type=Path); group.add_argument('--worker',type=Path); parser.add_argument('--mutant',action='store_true'); args=parser.parse_args()
    if args.worker: worker(args.worker,args.mutant); return
    original=(HERE/'ingress_store_model.c').read_text()
    variants=[('base',original),('limit',original.replace('UINT32_C(1039)','UINT32_C(1038)')),('byte',original.replace('byte_value & UINT32_C(255)','byte_value & UINT32_C(127)')),('branch',original.replace('index + 1u < (loaded_length','index + 1u <= (loaded_length'))]
    if any(text==original for _,text in variants[1:]): raise ValueError('mutation did not apply')
    with tempfile.TemporaryDirectory(prefix='tsl9-store-model-') as d:
        tmp=Path(d); batch=tmp/'build.bat'
        for label,flags in (('C','/TC /std:c11'),('Cpp','/TP /std:c++17')):
            for name,text in variants:
                src=tmp/(label+name+'.c'); dll=tmp/(label+name+'.dll'); src.write_text(text)
                batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{src}" /Fe:"{dll}"\n@exit /b %errorlevel%\n')
                subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=tmp,check=True)
                cmd=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)]
                if name!='base': cmd.append('--mutant')
                subprocess.run(cmd,check=True)

if __name__=='__main__': main()
