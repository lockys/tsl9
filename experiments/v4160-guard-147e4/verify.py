"""Bounded APP guard: real RV32 instruction fields vs C semantic projection.

No surrounding reachability, interrupts, faults, MMIO or physical RAM model.
The optional byte load is supplied by an independent successful-read stub.
"""
import argparse
import ctypes
import hashlib
from pathlib import Path
import random
import subprocess
import sys
import tempfile
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
BIN=ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
RAW=bytes.fromhex('1307f00f6399e712034714006315f712')
MASK=0xffffffff

def signed(value,bits): return value-(1<<bits) if value&(1<<(bits-1)) else value

def machine(image,a5,s0,byte):
    if image[0xc7e4:0xc7f4]!=RAW: raise ValueError('guard byte mismatch')
    regs=[0]*32; regs[15]=a5; regs[8]=s0; pc=0x147e4; read=address=0
    for _ in range(4):
        if pc in (0x1491a,0x147f4): break
        w=int.from_bytes(image[pc-0x8000:pc-0x8000+4],'little'); opcode=w&127; rd=w>>7&31; funct=w>>12&7; rs1=w>>15&31; rs2=w>>20&31
        if opcode==0x13 and funct==0:
            regs[rd]=(regs[rs1]+signed(w>>20,12))&MASK; pc+=4
        elif opcode==3 and funct==4:
            address=(regs[rs1]+signed(w>>20,12))&MASK; read=1; regs[rd]=byte; pc+=4
        elif opcode==0x63 and funct==1:
            imm=((w>>31&1)<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1)
            pc=(pc+signed(imm,13))&MASK if regs[rs1]!=regs[rs2] else pc+4
        else: raise ValueError(f'unsupported instruction {pc:#x}')
    if pc not in (0x1491a,0x147f4): raise ValueError('step limit')
    return (pc,read,address,regs[14])


def worker(dll):
    image=BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=SHA: raise ValueError('firmware identity mismatch')
    u=ctypes.c_uint32; fn=ctypes.CDLL(str(dll)).guard_147e4; fn.argtypes=[u,u,u,ctypes.POINTER(u)]; fn.restype=None
    rng=random.Random(0x416147e4); count=0
    def check(a5,s0,byte):
        nonlocal count
        out=(u*4)(); fn(a5,s0,byte,out); expected=machine(image,a5,s0,byte)
        if tuple(out)!=expected: raise ValueError(f'guard model mismatch: {a5:#x} {s0:#x} {byte:#x}')
        count+=1
    for byte in range(256):
        for a5 in range(256): check(a5,0xffffffff,byte)
    for n in range(20000):
        a5=rng.choice((255,0x1ff,rng.getrandbits(32))); check(a5,rng.getrandbits(32),rng.randrange(256))
    for pc in (0x147e4,0x147e8,0x147ec,0x147f0):
        bad=bytearray(image); bad[pc-0x8000]^=1
        try: machine(bad,255,0xffffffff,255)
        except ValueError as e:
            if str(e)=='guard byte mismatch': continue
        raise ValueError(f'mutant not rejected at {pc:#x}')
    print(f'PASS: {count} C vs decoded-instruction cases, all byte pairs, full a5 and address wrap; 4 instruction mutants rejected',flush=True)


def main():
    p=argparse.ArgumentParser(); g=p.add_mutually_exclusive_group(required=True); g.add_argument('--vcvars',type=Path); g.add_argument('--worker',type=Path); args=p.parse_args()
    if args.worker: worker(args.worker); return
    with tempfile.TemporaryDirectory(prefix='tsl9-147e4-') as temp:
        temp=Path(temp); batch=temp/'build.bat'
        def build(source,dll,flags):
            batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{source}" /Fe:"{dll}"\n@exit /b %errorlevel%\n',encoding='utf8')
            subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=temp,check=True)
        source=HERE/'model.c'
        for label,flags in (('C','/TC /std:c11'),('Cpp','/TP /std:c++17')):
            dll=temp/(label+'.dll'); build(source,dll,flags)
            subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)],check=True)
        original=source.read_text(encoding='utf8')
        for name,old,new in (('full_a5','incoming_a5 != 255','(incoming_a5 & 255u) != 255'),('read_address','s0 + 1u','s0 + 2u'),('sentinel','out[3] == incoming_a5','out[3] != incoming_a5')):
            if original.count(old)!=1: raise ValueError('ambiguous mutant')
            src=temp/(name+'.c'); dll=temp/(name+'.dll'); src.write_text(original.replace(old,new),encoding='utf8'); build(src,dll,'/TC /std:c11')
            result=subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)],capture_output=True,text=True)
            if result.returncode==0 or 'guard model mismatch' not in result.stderr: raise ValueError(f'mutant not detected: {name}\n{result.stderr}')
            print(f'PASS: {name} semantic mutant rejected',flush=True)
    print('APP bounded projection only; no reachability, real MMIO, fault or hardware claims.')

if __name__=='__main__': main()
