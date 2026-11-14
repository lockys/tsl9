#!/usr/bin/env python3
"""Bounded original-byte projection of the two GP+176 masked store windows."""
import argparse
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BASE=0x8000
MASK=0xffffffff
WINDOWS=((0xa0f2,bytes.fromhex('83c7010b85078d8b2388f10a')),(0xa33a,bytes.fromhex('83c7010b85078d8b22442388f10a')))
def need(ok,msg):
    if not ok:raise ValueError(msg)

def execute(code,gp,value,stack_word):
    registers=[0]*32;registers[3]=gp&MASK;registers[2]=0x20001000;pc=0;events=[]
    while pc<len(code):
        half=int.from_bytes(code[pc:pc+2],'little')
        if half&3!=3:
            if half==0x0785:registers[15]=(registers[15]+1)&MASK
            elif half==0x8b8d:registers[15]&=3
            elif half==0x4422:registers[8]=stack_word&MASK;events.append(('stack-read',registers[2]+8,4,stack_word&MASK))
            else:raise ValueError('unsupported compressed opcode')
            pc+=2;continue
        word=int.from_bytes(code[pc:pc+4],'little');opcode=word&0x7f;f3=(word>>12)&7;rs1=(word>>15)&31
        if opcode==3 and f3==4:
            rd=(word>>7)&31;imm=word>>20;need((rd,rs1,imm)==(15,3,176),'lbu operands')
            addr=(registers[rs1]+imm)&MASK;registers[rd]=value;events.append(('read',addr,1,value))
        elif opcode==0x23 and f3==0:
            rs2=(word>>20)&31;imm=((word>>25)<<5)|((word>>7)&31)
            need((rs1,rs2,imm)==(3,15,176),'store operands')
            addr=(registers[rs1]+imm)&MASK;events.append(('write',addr,1,registers[rs2]&255))
        else:raise ValueError('unsupported opcode')
        pc+=4
    need(pc==len(code),'instruction boundary')
    return events

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=ROOT)
    data=(parser.parse_args().root/BIN).read_bytes();need(len(data)==76800 and hashlib.sha256(data).hexdigest()==SHA,'APP identity')
    count=0
    for start,expected in WINDOWS:
        code=data[start-BASE:start-BASE+len(expected)];need(code==expected,'original window')
        for gp in (0,0x20004000,0xffffff50,0xffffffff):
            for value in range(256):
                for stack in (0,0xffffffff):
                    events=execute(code,gp,value,stack);addr=(gp+176)&MASK
                    want=[('read',addr,1,value)]
                    if start==0xa33a:want.append(('stack-read',0x20001008,4,stack))
                    want.append(('write',addr,1,(value+1)&3))
                    need(events==want,'event mismatch');count+=1
    print(f'PASS: {count} synthetic traces; 256 input bytes, four GP values and two stack values per window; exact instruction bytes pinned')
    print('LIMIT: local fall-through only, successful reads/writes and no interference assumed; stack is synthetic; no global writer, IRQ, ROM or hardware claim')

if __name__=='__main__':main()
