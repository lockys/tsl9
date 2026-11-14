"""Conditional success-path projection across guard, setter and precheck.

Reconstructed state at segment boundaries; 0x1070a is an unexecuted returning
stub assumed to preserve s0 and all input bytes. No alias, IRQ, traps, provider
side effects, whole-dispatcher reachability or hardware are asserted.
"""
import argparse
import ctypes
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
HERE=Path(__file__).resolve().parent; OTHER=HERE.parent/'v4160-dispatch-148b4-model'

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); obj=importlib.util.module_from_spec(spec); spec.loader.exec_module(obj); return obj
prefix=load('prefix',OTHER/'payload_gate.py'); setter=load('setter',OTHER/'state_setter.py'); predecessor=load('predecessor',OTHER/'predecessor.py'); entry=load('entry',OTHER/'entry_provenance.py')


def worker(dll):
    image=prefix.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=prefix.SHA: raise ValueError('firmware identity mismatch')
    if tuple(entry.jal_target(pc,entry.read_at(image,pc,4)) for pc in (0x147f8,0x147fc))!=(0x13ba6,0x1070a): raise ValueError('call target mismatch')
    u=ctypes.c_uint32; fn=ctypes.CDLL(str(dll)).guard_147e4; fn.argtypes=[u,u,u,ctypes.POINTER(u)]; fn.restype=None
    base=0x20001000; handle=0x1234; window=image[0xc800:0xc812]
    if window!=bytes.fromhex('8357240005676384e70209676386e70285ef'): raise ValueError('precheck bytes mismatch')
    pc,reads,trace,regs=prefix.run(image,20,255,255,base,handle)
    if pc!=0x147f8 or reads!=[base,base+1] or 0x147e4 not in trace or (regs[10],regs[11],regs[8])!=(handle,2,base): raise ValueError('prefix boundary mismatch')
    out=(u*4)(); fn(255,base,255,out)
    if tuple(out)!=(0x147f4,1,base+1,255): raise ValueError('guard boundary mismatch')
    for first,second,expect in ((handle,handle,[(0x2000c799,2)]),(0,handle,[(0x2000c79d,2)]),(0,1,[])):
        _,writes,regs=setter.run(image,handle,2,first,second)
        if writes!=expect or regs[2:]!=(handle,2): raise ValueError('setter boundary mismatch')
    counts={}
    for halfword in range(65536):
        pc,address=predecessor.run(window,halfword,base)
        expect=0x14812 if halfword==0 else 0x1482e if halfword==0x1000 else 0x14838 if halfword==0x2000 else 0x14848
        if pc!=expect or address!=base+2: raise ValueError('halfword precheck mismatch')
        counts[pc]=counts.get(pc,0)+1
    if counts!={0x14812:1,0x1482e:1,0x14838:1,0x14848:65533}: raise ValueError('unexpected precheck totals')
    print('PASS: guard success, first/second/no matching setter and 65536 subsequent halfword prechecks',flush=True)
    print('Conditional segment composition only; callback 0x1070a not executed, no reachability or hardware claim.')


def main():
    p=argparse.ArgumentParser(); g=p.add_mutually_exclusive_group(required=True); g.add_argument('--vcvars',type=Path); g.add_argument('--worker',type=Path); args=p.parse_args()
    if args.worker: worker(args.worker); return
    with tempfile.TemporaryDirectory(prefix='tsl9-guard-success-') as d:
        tmp=Path(d); batch=tmp/'build.bat'
        for label,flags in (('C','/TC /std:c11'),('Cpp','/TP /std:c++17')):
            dll=tmp/(label+'.dll'); batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{HERE / "model.c"}" /Fe:"{dll}"\n@exit /b %errorlevel%\n',encoding='utf8')
            subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=tmp,check=True)
            subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)],check=True)

if __name__=='__main__': main()
