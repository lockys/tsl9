"""Compare C byte-transfer projection against bounded original-PC events."""
import argparse
import ctypes
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('bytepath',HERE/'transfer_byte_path.py')
bytepath=importlib.util.module_from_spec(spec); spec.loader.exec_module(bytepath)


def worker(dll,mutant):
    original=bytepath.original
    image=original.mod.entry.calls.case.dispatch.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=original.mod.entry.calls.case.dispatch.SHA: raise ValueError('APP identity mismatch')
    evidence=json.loads(original.EVIDENCE.read_text(encoding='utf-8'))
    ops=next(x['operations'] for x in evidence['functions'] if x['start']==original.START)
    original.validate(image,ops)
    u=ctypes.c_uint32; byte=ctypes.c_uint8
    fn=ctypes.CDLL(str(dll)).tsl9_byte_transfer; fn.argtypes=[ctypes.POINTER(byte),u,u,u]; fn.restype=u
    def check(src,dst,length):
        expected={i:(i*37+11)&255 for i in range(64)}
        events,_,_=bytepath.execute(image,ops,expected,dst,src,length)
        memory=(byte*64)(*[((i*37+11)&255) for i in range(64)])
        n=fn(memory,src,dst,length)
        return n==len(events)//2 and bytes(memory)==bytes(expected.values())
    if mutant:
        if all(check(*x) for x in ((0,1,0),(0,1,4),(0,16,4),(3,0xffffffff,1))): raise ValueError('mutant accepted')
        print('PASS: mutant rejected',flush=True); return
    for dst in range(8,24):
        for src in range(8,24):
            for length in range(17):
                if not check(src,dst,length): raise ValueError('transfer mismatch')
    for dst,length in ((0xffffffff,1),(0xfffffffe,2),(0xfffffff0,16),(0xffffffff,0xffffffff)):
        if not check(7,dst,length): raise ValueError('wrap mismatch')
    print('PASS: 4352 C/PC-projection cases and 4 wrapped-end checks',flush=True)


def main():
    p=argparse.ArgumentParser(); group=p.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars',type=Path); group.add_argument('--worker',type=Path); p.add_argument('--mutant',action='store_true'); args=p.parse_args()
    if args.worker: worker(args.worker,args.mutant); return
    source=(HERE/'transfer_byte_model.c').read_text(encoding='utf-8')
    variants=[('base',source)]
    for name,old,new in (('return','return length;','return 0;'),('loop','dst<end','dst+1<end'),('increment','++src;','src+=2;')):
        if source.count(old)!=1: raise ValueError('ambiguous mutation')
        variants.append((name,source.replace(old,new)))
    with tempfile.TemporaryDirectory(prefix='tsl9-byte-') as temp:
        folder=Path(temp)
        for label,flags in (('C','/TC /std:c11'),('Cpp','/TP /std:c++17')):
            for name,text in variants:
                src=folder/(label+name+'.c'); dll=folder/(label+name+'.dll'); batch=folder/'build.bat'; src.write_text(text,encoding='utf-8')
                batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{src}" /Fe:"{dll}"\n@exit /b %errorlevel%\n',encoding='utf-8')
                subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=folder,check=True)
                cmd=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)]
                if name!='base': cmd.append('--mutant')
                subprocess.run(cmd,check=True)
    print('Model inputs assume successful, in-range accesses when the loop executes; not an ISA or hardware test.')

if __name__=='__main__': main()
