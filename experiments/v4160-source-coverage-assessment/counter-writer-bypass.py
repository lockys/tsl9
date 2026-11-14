#!/usr/bin/env python3
"""Bounded APP branch projection around the GP+176 masked writer."""
import argparse,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
WINDOWS=((0xa0e6,'83c7a10a6386a7102385a10a83c7010b85078d8b2388f10a61cd'),(0xa1e2,'83c7f10a9df7'),(0xa1f6,'e39f07f0e5b7'))
def need(v,msg):
    if not v:raise ValueError(msg)
def branch32(pc,word):
    need(word&127==0x63,'branch opcode')
    imm=((word>>31)&1)<<12|((word>>7)&1)<<11|((word>>25)&63)<<5|((word>>8)&15)<<1
    return (pc+(imm-8192 if imm&4096 else imm))&0xffffffff
def projection(old,current,counter,aux):
    # At 0xa0ea a5 is zero-extended byte; a0 is the full return word.
    if old==current:
        if old:return (0xa114,counter,False)
        return (0xa114 if aux else 0xa1e8,counter,False)
    counter=(counter+1)&3
    return (0xa100 if current else 0xa1d6,counter,True)
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);root=p.parse_args().root
    data=(root/BIN).read_bytes();need(len(data)==76800 and hashlib.sha256(data).hexdigest()==SHA,'APP identity')
    for pc,h in WINDOWS:
        b=bytes.fromhex(h);need(data[pc-0x8000:pc-0x8000+len(b)]==b,'instruction bytes')
    need(branch32(0xa0ea,int.from_bytes(data[0xa0ea-0x8000:0xa0ee-0x8000],'little'))==0xa1f6,'equal branch')
    need(branch32(0xa1f6,int.from_bytes(data[0xa1f6-0x8000:0xa1fa-0x8000],'little'))==0xa114,'nonzero branch')
    bypass=0
    for old in range(256):
        for current in range(256):
            for aux in (0,1):
                pc,counter,wrote=projection(old,current,255,aux)
                if old==current:
                    need(not wrote and counter==255,'equal must bypass writer')
                    need(pc==(0xa114 if old or aux else 0xa1e8),'equal route');bypass+=pc==0xa114
                else:need(wrote and counter==0 and pc==(0xa100 if current else 0xa1d6),'different must mask')
    for current in (256,0x10000,0xffffffff):
        for old in range(256):need(projection(old,current,255,0)==(0xa100,0,True),'full-width comparison')
    print(f'PASS: 131072 byte pairs/aux cases, 768 full-width cases; {bypass} equal cases bypass the masked writer to 0xa114')
    print('LIMIT: fixed-byte local projection, synthetic counter=255 and successful accesses; later calls, 0xa146 reachability, interrupts and hardware are not modelled')
if __name__=='__main__':main()
