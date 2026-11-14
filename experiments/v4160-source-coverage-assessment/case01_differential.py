"""C case 0/1 event projection against bounded original instruction components."""
import argparse
import ctypes
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('composition',HERE/'case01_setter.py')
composition=importlib.util.module_from_spec(spec); spec.loader.exec_module(composition)


def worker(dll,mutant):
    setter=composition.setter
    image=setter.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=setter.SHA: raise ValueError('APP identity mismatch')
    u=ctypes.c_uint32; fn=ctypes.CDLL(str(dll)).tsl9_case01
    fn.argtypes=[u,u,u,u,ctypes.POINTER(u)]; fn.restype=None
    def compare(index,handle,first,second):
        (target,a0,a1,_),(target2,arg2,_),_=composition.calls.run(image,index,handle)
        if target!=0x13ba6: raise ValueError('first callee mismatch')
        _,writes,_=setter.run(image,a0,a1,first,second)
        want=[0,0,0,target2,arg2]
        if writes: want=[1,*writes[0],target2,arg2]
        result=(u*5)(); fn(index,handle,first,second,result)
        return list(result)==want
    if mutant:
        cases=((0,5,5,5),(1,5,5,5),(1,5,4,5),(1,5,4,4),(1,0x10005,5,5))
        if all(compare(*c) for c in cases): raise ValueError('mutant not detected')
        print('PASS: semantic mutant rejected',flush=True); return
    for index in (0,1):
        for first in range(65536):
            for handle,second in ((first,first),(first^1,first^1),(first^1,first),(first|0x10000,first)):
                if not compare(index,handle,first,second): raise ValueError('projection mismatch')
    print('PASS: 524288 C/original-projection comparisons',flush=True)


def main():
    parser=argparse.ArgumentParser(); group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars',type=Path); group.add_argument('--worker',type=Path); parser.add_argument('--mutant',action='store_true'); args=parser.parse_args()
    if args.worker: worker(args.worker,args.mutant); return
    source=(HERE/'case01_model.c').read_text(encoding='utf-8'); variants=[('base',source)]
    changes=(('mode','0u : 3u','0u : 4u'),('first','0x2000c799','0x2000c798'),('second','0x2000c79d','0x2000c79c'),('next','0u : 2u','0u : 3u'),('width','handle == first','(handle & 0xffffu) == first'))
    for name,old,new in changes:
        if source.count(old)!=1: raise ValueError('ambiguous mutant')
        variants.append((name,source.replace(old,new)))
    with tempfile.TemporaryDirectory(prefix='tsl9-case01-') as temp:
        folder=Path(temp)
        for label,flags in (('C','/TC /std:c11'),('Cpp','/TP /std:c++17')):
            for name,text in variants:
                src=folder/(label+name+'.c'); dll=folder/(label+name+'.dll'); batch=folder/'build.bat'; src.write_text(text,encoding='utf-8')
                batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{src}" /Fe:"{dll}"\n@exit /b %errorlevel%\n',encoding='utf-8')
                subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=folder,check=True)
                cmd=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)]
                if name!='base': cmd.append('--mutant')
                subprocess.run(cmd,check=True)
    print('Successful reads and leaf return assumed; 0x12ad0 not executed.')

if __name__=='__main__': main()
