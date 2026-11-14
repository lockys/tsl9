#!/usr/bin/env python3
"""Identify selected GP+128 address preparations and indirect call slots, not reachability."""
import hashlib
from pathlib import Path
import argparse
ROOT=Path(__file__).resolve().parents[2]
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
SITES=((0x86cc,0x86dc,0x86e0,23,316),(0x87c0,0x87bc,0x87c6,23,316),(0x8a8a,0x8a86,0x8a8e,15,316),(0x8aae,0x8aaa,0x8ab4,15,316),(0x8fb0,0x8faa,0x8fb6,8,312))
def need(condition,message):
    if not condition:raise ValueError(message)
def decode_i(w):
    imm=w>>20
    return w&127,(w>>7)&31,(w>>12)&7,(w>>15)&31,imm-4096 if imm&2048 else imm

def check(data):
    need(len(data)==76800 and hashlib.sha256(data).hexdigest()==SHA,'APP identity')
    def read(pc,n):return data[pc-0x8000:pc-0x8000+n]
    need(read(0x86c8,4)==bytes.fromhex('b70b0400'),'s7 base instruction')
    need(read(0x8f5e,4)==bytes.fromhex('37040400'),'s0 base instruction')
    for setup,load,call,base,offset in SITES:
        w=int.from_bytes(read(setup,4),'little');need(decode_i(w)==(0x13,11,0,3,128),'a1 setup')
        w=int.from_bytes(read(load,4),'little');need(decode_i(w)==(3,15,2,base,offset),'slot load')
        need(read(call,2)==bytes.fromhex('8297'),'indirect call')
    return len(SITES)
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);a=p.parse_args()
    n=check((a.root/BIN).read_bytes())
    print(f'PASS: {n} pinned GP+128 preparations, slot loads and indirect calls')
    print('LIMIT: slot bases live at loads are assumed 0x40000; no path, register liveness, resident identity, retained pointer or hardware proven')
if __name__=='__main__':main()
