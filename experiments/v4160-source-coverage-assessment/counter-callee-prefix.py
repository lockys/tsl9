#!/usr/bin/env python3
"""Static verification of three local caller argument setups, not resident behavior."""
import argparse
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
MASK=0xffffffff
WINDOWS=((0x12506,'797122d4370404003c444ad017a9ff1f130929ac06d626d24ece4a85614681458297'),(0x12528,'3c4497a4ff1f938424ac13064002814526858297'),(0x175e8,'797122d4370404003c4426d29754ff1f9384c41a06d61306c010814526858297'))
PAIRS=((0x12512,0x12516,18,0x2000bfd4,24),(0x1252a,0x1252e,9,0x2000bfec,36),(0x175f4,0x175f8,9,0x2000c7a0,268))
def need(ok,msg):
    if not ok:raise ValueError(msg)
def check(data):
    need(len(data)==76800 and hashlib.sha256(data).hexdigest()==SHA,'original BIN identity')
    def read(pc,n):return data[pc-0x8000:pc-0x8000+n]
    for start,hexbytes in WINDOWS:need(read(start,len(bytes.fromhex(hexbytes)))==bytes.fromhex(hexbytes),'fixed instruction window')
    for pc,addpc,reg,dest,size in PAIRS:
        au=int.from_bytes(read(pc,4),'little');ad=int.from_bytes(read(addpc,4),'little')
        need((au&127,(au>>7)&31)==(0x17,reg),'auipc operands')
        need((ad&127,(ad>>7)&31,(ad>>12)&7,(ad>>15)&31)==(0x13,reg,0,reg),'addi operands')
        imm=ad>>20;imm=imm-4096 if imm&2048 else imm
        actual=(pc+(au&0xfffff000)+imm)&MASK
        need(actual==dest,'PC-relative destination')
        need(not(dest<=0x200040b0<dest+size),'conditional ranges overlap counter')
    return len(PAIRS)
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);root=p.parse_args().root
    print('PASS:',check((root/BIN).read_bytes()),'pinned call setups; decoded PC-relative destinations and conditional disjoint ranges')
    print('LIMIT: provider identity, memory effects, stack alias, register preservation, caller reachability and hardware not proven')
if __name__=='__main__':main()
