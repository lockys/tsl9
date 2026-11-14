#!/usr/bin/env python3
"""Synthetic read-after-copy alias witness at APP 0x82d2 packaging boundary."""
import argparse,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
def need(v,msg):
    if not v:raise ValueError(msg)
def run(payload,overlap):
    # Independent linear byte memory. The chosen aligned SP is synthetic.
    memory=bytearray(256);sp=0x40;record=sp+4 if overlap else 0x80
    memory[record:record+12]=bytes((0x70,3,8,payload,0x21,0x22,0x23,0x24,0x25,0x26,0x27,0))
    ident=memory[record]|memory[record+1]<<8;flag=memory[record+11];length=memory[record+2]
    need(length==8,'entry length')
    memory[sp+5]=ident&255;memory[sp+4]=((ident>>8)|(flag<<4))&255
    # Hypothesis only: normally returning forward byte-copy provider with
    # preserved s0/s1/sp; source and destination are read at each byte.
    for i in range(length):memory[sp+6+i]=memory[record+3+i]
    return memory[record+2],memory[record+2]+2,bytes(memory[sp+4:sp+14])
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=ROOT);img=(ap.parse_args().root/BIN).read_bytes()
    need(len(img)==76800 and hashlib.sha256(img).hexdigest()==SHA,'APP identity')
    for pc,h in ((0x8332,'83d6040083c7b400e285a302d1001397470093d78600d98f2302f10083a7cc0413056100829783c62400'),(0x82fe,'a14b130c3500')):
        b=bytes.fromhex(h);need(img[pc-0x8000:pc-0x8000+len(b)]==b,f'instruction mismatch {pc:x}')
    for value in range(256):
        alias=run(value,True);separate=run(value,False)
        need(alias[0:2]==(value,value+2),'alias reread')
        need(separate[0:2]==(8,10),'nonalias control')
    # For the documented queue call and normal stack discipline, record is
    # precheck SP+72, whereas copy destination begins at precheck SP+6.
    need(set(range(6,14)).isdisjoint(range(72,84)),'queue stack separation')
    print('PASS: 256 aliased and 256 disjoint synthetic memory cases; post-copy length may change from 8 to any byte')
    print('Queue-call projection: SP+6..13 is disjoint from record SP+72..83, so this synthetic alias is excluded when the frames are preserved.')
    print('LIMIT: assumes record=SP+4 and forward-copy provider, stable preserved registers, successful reads/writes and no interrupts; this alias is not the normal queue stack layout; installed provider and reachability unverified')
if __name__=='__main__':main()
