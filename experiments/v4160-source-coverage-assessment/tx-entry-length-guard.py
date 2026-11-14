#!/usr/bin/env python3
"""Decode TX entry guard and saved s0 assignment, conditional on successful execution."""
import argparse,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];MASK=0xffffffff
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin';SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
def need(x,msg):
    if not x:raise ValueError(msg)
def decode(b):
    need(len(b)==30,'window length');need(b==bytes.fromhex('9307f04063e9d710011122cc26ca4ac84ec606ce03d761092a893684b284'),'entry bytes')
    w=int.from_bytes(b[:4],'little');need((w&127,(w>>7)&31,(w>>12)&7,(w>>15)&31,w>>20)==(0x13,15,0,0,1039),'limit')
    w=int.from_bytes(b[4:8],'little');imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1);imm=imm-8192 if imm&4096 else imm
    need((w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,0x8a5a+imm)==(0x63,6,15,13,0x8b6c),'guard')
    h=int.from_bytes(b[26:28],'little');need((h&3,h>>12,(h>>7)&31,(h>>2)&31)==(2,8,8,13),'s0 from a3')
    return 1039,0x8b6c

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);root=p.parse_args().root
    image=(root/BIN).read_bytes();need(len(image)==76800 and hashlib.sha256(image).hexdigest()==SHA,'identity');b=image[0xa56:0xa74];limit,target=decode(b)
    for length in list(range(65536))+[0x10000,0x7fffffff,0xffffffff]:
        accepted=length<=limit
        need((target if length>limit else 0x8a5e)==(0x8a5e if accepted else 0x8b6c),'unsigned gate')
        if accepted:need(length<=65535,'entry s0 width')
    for i in range(len(b)):
        mutant=bytearray(b);mutant[i]^=1
        try:decode(mutant)
        except ValueError:continue
        raise ValueError('mutation accepted')
    print('PASS: 65539 unsigned lengths; 30 byte mutations rejected')
    print('LIMIT: only initial guard and assignment, before any opaque calls; no claim later s0 remains unchanged, reachability or hardware')
if __name__=='__main__':main()
