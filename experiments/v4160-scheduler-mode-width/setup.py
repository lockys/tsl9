"""Decode scheduler's table address materialization and general-path setup.

Projection from 0x9132 to branch, and separately 0x9188 to 0x9196.
No stack prologue, scan, traps, concurrency or provider execution.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v',HERE/'verify.py'); v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
MASK=0xffffffff
OPS={0x9132:'17390020',0x9136:'130969cd',0x9188:'97370020',0x918c:'938707c8',0x9190:'368a',0x9192:'b289',0x9194:'2e84'}


def auipc(image,pc,rd):
    word=int.from_bytes(image[pc-0x8000:pc-0x8000+4],'little')
    if word&0x7f!=0x17 or (word>>7)&31!=rd: raise ValueError('bad auipc')
    return (pc+(word&0xfffff000))&MASK


def addi(image,pc,rd,rs1,value):
    word=int.from_bytes(image[pc-0x8000:pc-0x8000+4],'little')
    if word&0x7f!=0x13 or (word>>12)&7!=0 or (word>>7)&31!=rd or (word>>15)&31!=rs1: raise ValueError('bad addi')
    imm=word>>20
    if imm&0x800: imm-=4096
    return (value+imm)&MASK


def run(image,callback,mode,delay,argument):
    if any(not 0<=x<=MASK for x in (callback,mode,delay,argument)): raise ValueError('bad input')
    for pc,encoded in OPS.items():
        value=bytes.fromhex(encoded); off=pc-0x8000
        if image[off:off+len(value)]!=value: raise ValueError(f'opcode mismatch {pc:#x}')
    s2=addi(image,0x9136,18,18,auipc(image,0x9132,18))
    a5=addi(image,0x918c,15,15,auipc(image,0x9188,15))
    # C.MV s4,a3; C.MV s3,a2; C.MV s0,a1.
    s4=argument; s3=delay; s0=mode
    return callback,s0,s2,s3,s4,a5


def main():
    image=v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=v.SHA: raise ValueError('firmware identity mismatch')
    for x in range(65536):
        args=(x*65537& MASK,x,((x*0x10001)^0x80000000)&MASK,(~x)&MASK)
        if run(image,*args)!=(args[0],args[1],0x2000be08,args[2],args[3],0x2000be08): raise ValueError('setup mismatch')
    for pc in OPS:
        changed=bytearray(image); changed[pc-0x8000]^=1
        try: run(changed,0,0,0,0)
        except ValueError: continue
        raise ValueError(f'mutant accepted {pc:#x}')
    # Verify independently decoded immediate/operand guards with modifications
    # that retain some opcodes, without relying on OPS equality in run().
    for pc,decoder in ((0x9132,lambda b: auipc(b,0x9132,18)),(0x9136,lambda b: addi(b,0x9136,18,18,0))):
        changed=bytearray(image); changed[pc-0x8000]^=0x80
        try: decoder(changed)
        except ValueError: continue
        raise ValueError('operand mutant accepted')
    print('PASS: 65536 synthetic setups; both independently PC-relative bases = 0x2000be08')
    print('PASS: 7 instruction mutations and 2 decoded operand mutations rejected')
    print('Projection only; no prologue, calls, provider, memory effects or hardware execution.')

if __name__=='__main__': main()
