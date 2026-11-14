#!/usr/bin/env python3
"""Address-only counter alias envelope for two original prologue stack frames."""
import argparse
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
MASK=0xffffffff
TARGET=0x200040b0
# Offsets are from post-prologue SP; these stores precede first indirect call.
FRAMES=((0x12506,bytes.fromhex('797122d4370404003c444ad017a9ff1f130929ac06d626d24ece4a85614681458297'),(40,32,44,36,28)),(0x175e8,bytes.fromhex('797122d4370404003c4426d29754ff1f9384c41a06d61306c010814526858297'),(40,36,44)))
def need(ok,msg):
    if not ok:raise ValueError(msg)
def overlapping(initial_sp,offsets,target=TARGET):
    frame=(initial_sp-48)&MASK
    return tuple(o for o in offsets if any(((frame+o+i)&MASK)==target for i in range(4)))
def inverse(offsets,target=TARGET):
    return {((target+48-o-i)&MASK) for o in offsets for i in range(4)}
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);root=p.parse_args().root
    data=(root/BIN).read_bytes();need(len(data)==76800 and hashlib.sha256(data).hexdigest()==SHA,'APP identity')
    checks=0
    for pc,expected,offsets in FRAMES:
        need(data[pc-0x8000:pc-0x8000+len(expected)]==expected,'instruction window')
        candidates=inverse(offsets)
        for target in (TARGET,0,0xffffffff,0x40048):
            candidates=inverse(offsets,target)
            # The preimage is exactly the union of each store's four modular byte addresses.
            for sp in candidates|{(x+d)&MASK for x in candidates for d in (-1,1,16,-16)}:
                need(bool(overlapping(sp,offsets,target))==(sp in candidates),'inverse mismatch');checks+=1
        aligned=sorted(x for x in inverse(offsets) if x%4==0)
        expected_aligned=[TARGET+v for v in ((4,8,12,16,20) if pc==0x12506 else (4,8,12))]
        need(aligned==expected_aligned,'aligned SP witness')
        print(f'0x{pc:x}: aligned incoming SP aliases counter at '+', '.join(f'0x{x:08x}' for x in aligned))
    print(f'PASS: {checks} modular SP/target boundary cases; APP windows pinned')
    print('LIMIT: address-only synthetic witnesses, not successful aligned accesses, register values, actual SP, reachability, or hardware')
if __name__=='__main__':main()
