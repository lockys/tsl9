#!/usr/bin/env python3
"""Prove relative stack ranges under the documented queue call assumptions."""
import argparse,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
MASK=0xffffffff
def need(v,msg):
    if not v:raise ValueError(msg)
def addr(sp,offset):return (sp+offset)&MASK
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/BIN).read_bytes()
    need(len(image)==76800 and hashlib.sha256(image).hexdigest()==SHA,'APP identity')
    # Queue frame allocation, record argument, precheck frame allocation,
    # source pointer and destination pointer, respectively.
    for pc,h in ((0x12c58,'5d71'),(0x12cae,'2800ef502fe2'),(0x82d2,'3971'),(0x8300,'130c3500'),(0x8352,'130561008297')):
        b=bytes.fromhex(h);need(image[pc-0x8000:pc-0x8000+len(b)]==b,f'instruction mismatch {pc:x}')
    # Queue SP = precheck SP+64; argument is queue SP+8. Source is
    # record+3, destination is precheck SP+6; length at call <=8.
    for n in range(9):
        dest=set(range(6,6+n));record=set(range(72,84));source=set(range(75,75+n))
        need(dest.isdisjoint(record) and dest.isdisjoint(source),'relative overlap')
    for sp in list(range(0,65536))+[0xfffffff0,0xfffffffa,0xffffffff,0x2000fff0]:
        dest={addr(sp,x) for x in range(6,14)};record={addr(sp,x) for x in range(72,84)}
        need(dest.isdisjoint(record),'modular overlap')
    print('PASS: lengths 0..8, 65540 synthetic SP values including modular wrap; no relative destination/record overlap')
    print('LIMIT: queue SP and precheck SP must follow the pinned frames, and registers/provider behavior must preserve these pointers; physical memory, interrupts and reachability unverified')
if __name__=='__main__':main()
