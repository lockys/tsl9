#!/usr/bin/env python3
"""Conditional V1.31 reference CCC clear versus APP GP+176 counter."""
import argparse
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
APP='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
APP_SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
REF='analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin'
REF_SHA='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'
COUNTER=0x200040b0
BASE=0x20004080
WINDOWS=((0x40138,'d0cf0400'),(0x4cfd0,'c167fd176315f5002e856fe02fb6411106c6efe02fb009c5fd571ea123010500b24041018280'),(0x4b33c,'b737002003c7573bfd56814763e3e700828016a12301050085071105c5bf'))
def need(value,message):
    if not value:raise ValueError(message)
def project(capacity):
    # Conditional Xwchc qk.c.sh: each record writes ff ff 00; pad is untouched.
    memory=bytearray([0x5a]*1024)
    memory[48]=1  # Start inside the alleged 0..3 invariant.
    for i in range(capacity):memory[4*i:4*i+3]=b'\xff\xff\x00'
    return memory

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);root=p.parse_args().root
    app=(root/APP).read_bytes();need(len(app)==76800 and hashlib.sha256(app).hexdigest()==APP_SHA,'APP identity')
    need(app[0x8faa-0x8000:0x8fb8-0x8000]==bytes.fromhex('832784134165938501087d158297'),'APP call-site bytes')
    path=root/REF
    if not path.exists():raise SystemExit('SKIP (nonzero): reference carrier unavailable')
    ref=path.read_bytes();need(hashlib.sha256(ref).hexdigest()==REF_SHA,'reference identity')
    for pc,h in WINDOWS:
        expected=bytes.fromhex(h);need(ref[pc-0x40000:pc-0x40000+len(expected)]==expected,'reference window')
    offset=COUNTER-BASE;need(offset==48,'counter position')
    for cap in range(256):
        data=project(cap)
        need(data[offset]==(0xff if cap>=13 else 1),'counter result')
        for i in range(255):
            expected=(b'\xff\xff\x00\x5a' if i<cap else (b'\x01\x5a\x5a\x5a' if i==12 else b'\x5a'*4))
            need(data[4*i:4*i+4]==expected,'record bytes')
    print('PASS: all 256 capacities, 255 records each; record 12 first byte becomes 0xff iff capacity >= 13')
    print('LIMIT: reference V1.31 only; conditional Xwchc/slot identity, unchanged GP, stable capacity, successful accesses and no interference; no hardware reachability claim')
if __name__=='__main__':main()
