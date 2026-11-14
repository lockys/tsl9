"""C bulk-step projection against fixed-PC shared-memory projection."""
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
spec=importlib.util.spec_from_file_location('bulk',HERE/'transfer_bulk_step.py')
bulk=importlib.util.module_from_spec(spec); spec.loader.exec_module(bulk)


def worker(dll,mutant):
    original=bulk.original
    image=original.mod.entry.calls.case.dispatch.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=original.mod.entry.calls.case.dispatch.SHA: raise ValueError('APP identity mismatch')
    evidence=json.loads(original.EVIDENCE.read_text(encoding='utf-8'))
    original.validate(image,next(x['operations'] for x in evidence['functions'] if x['start']==original.START))
    byte=ctypes.c_uint8; u=ctypes.c_uint32
    fn=ctypes.CDLL(str(dll)).tsl9_bulk_step; fn.argtypes=[ctypes.POINTER(byte),u,u]; fn.restype=None
    def check(src,dst,seed):
        expected={i:(i*73+seed)&255 for i in range(160)}
        _,_,_=bulk.step(expected,src,dst)
        memory=(byte*160)(*[((i*73+seed)&255) for i in range(160)])
        fn(memory,src,dst)
        return bytes(memory)==bytes(expected.values())
    if mutant:
        if all(check(*x) for x in ((32,64,19),(32,100,19),(64,32,13))): raise ValueError('mutant accepted')
        print('PASS: semantic mutant rejected',flush=True); return
    for src in range(32,96,4):
        for dst in range(32,96,4):
            for seed in range(256):
                if not check(src,dst,seed): raise ValueError('shared-memory mismatch')
    print('PASS: 65536 aligned shared-memory C/projection cases',flush=True)


def main():
    parser=argparse.ArgumentParser(); group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars',type=Path); group.add_argument('--worker',type=Path); parser.add_argument('--mutant',action='store_true'); args=parser.parse_args()
    if args.worker: worker(args.worker,args.mutant); return
    source=(HERE/'transfer_bulk_model.c').read_text(encoding='utf-8'); variants=[('base',source)]
    changes=(('early_ninth','    write32(memory+dst,w[0]);\n    w[8]=read32(memory+src+32);','    w[8]=read32(memory+src+32);\n    write32(memory+dst,w[0]);'),('last_word','i<9','i<8'),('wrong_offset','memory+src+32','memory+src+28'))
    for name,old,new in changes:
        if source.count(old)!=1: raise ValueError('ambiguous mutant')
        variants.append((name,source.replace(old,new)))
    with tempfile.TemporaryDirectory(prefix='tsl9-bulk-') as temp:
        folder=Path(temp)
        for label,flags in (('C','/TC /std:c11'),('Cpp','/TP /std:c++17')):
            for name,text in variants:
                src=folder/(label+name+'.c'); dll=folder/(label+name+'.dll'); batch=folder/'build.bat'; src.write_text(text,encoding='utf-8')
                batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{src}" /Fe:"{dll}"\n@exit /b %errorlevel%\n',encoding='utf-8')
                subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=folder,check=True)
                cmd=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)]
                if name!='base': cmd.append('--mutant')
                subprocess.run(cmd,check=True)
    print('Single step; aligned successful accesses assumed, not CPU or hardware execution.')

if __name__=='__main__': main()
