#!/usr/bin/env python3
"""Analyze information loss in the conditional 0x82d2 header projection."""
import argparse,hashlib
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
def need(v,msg):
    if not v:raise ValueError(msg)
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/BIN).read_bytes()
    need(len(image)==76800 and hashlib.sha256(image).hexdigest()==SHA,'APP identity')
    pc=0x8332;b=bytes.fromhex('83d6040083c7b400e285a302d1001397470093d78600d98f2302f100')
    need(image[pc-0x8000:pc-0x8000+len(b)]==b,'instruction mismatch')
    classes=Counter()
    for hi in range(256):
        # Full flag byte is loaded; its upper nibble disappears in the SB.
        outputs=Counter((hi|(flag<<4))&255 for flag in range(256))
        bits=(hi>>4).bit_count();classes[bits]+=1
        need(len(outputs)==1<<(4-bits),'distinct output count')
        need(set(outputs.values())=={16*(1<<bits)},'preimage multiplicity')
        need(all((out&15)==(hi&15) for out in outputs),'identifier low nibble')
    need([classes[i] for i in range(5)]==[16,64,96,64,16],'binomial distribution')
    need(len({(3|(flag<<4))&255 for flag in range(256)})==16,'0370 nibble preservation')
    print('PASS: all 65536 identifier-high-byte/flag pairs; distinct outputs per identifier: 16, 8, 4, 2 or 1')
    print('Identifier-high-byte counts for these classes: 16, 64, 96, 64, 16; identifier 0x0370 retains the low flag nibble')
    print('LIMIT: conditional successful local path only; no reachability, physical memory, provider or receiver interpretation established')
if __name__=='__main__':main()
