#!/usr/bin/env python3
"""Decode original TX checksum store at 0x8b14; event projection only."""
import argparse,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];MASK=0xffffffff
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin';SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
def need(v,msg):
    if not v:raise ValueError(msg)
def decode(b):
    need(len(b)==6 and b==bytes.fromhex('a297a382e700'),'window')
    c=int.from_bytes(b[:2],'little');need((c&3,(c>>12)&15,(c>>7)&31,(c>>2)&31)==(2,9,15,8),'c.add a5,s0')
    w=int.from_bytes(b[2:],'little');imm=((w>>25)<<5)|((w>>7)&31);need((w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,imm)==(0x23,0,15,14,5),'sb a4,5(a5)')
def project(a5,s0,a4):return ((a5+s0+5)&MASK,1,a4&255)
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/BIN).read_bytes()
    need(len(image)==76800 and hashlib.sha256(image).hexdigest()==SHA,'identity');raw=image[0xb14:0xb1a];decode(raw)
    for a4 in range(65536):
        for addr,n in ((0,0),(0xfffffff9,2),(0xffffffff,0xffffffff),(0x2000b192,1039)):
            event=project(addr,n,a4);need(event==((addr+n+5)&MASK,1,a4%256),'projection')
    for i in range(6):
        x=bytearray(raw);x[i]^=1
        try:decode(x)
        except ValueError:continue
        raise ValueError('mutation accepted')
    print('PASS: 262144 checksum store projections, 6 mutations rejected')
    print('LIMIT: then-live registers, successful byte store, no concurrency or faults assumed; no physical write, full tail or reachability proof')
if __name__=='__main__':main()
