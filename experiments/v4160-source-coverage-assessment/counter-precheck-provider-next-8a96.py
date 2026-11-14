#!/usr/bin/env python3
"""Bounded 0x8a96 load/compare following the provider call."""
import argparse,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
CODE=bytes.fromhex('83d7a10963922703');MASK=0xffffffff
def need(value,message):
    if not value:raise ValueError(message)
def decode(code):
    need(code==CODE,'instruction mismatch')
    l=int.from_bytes(code[:4],'little');b=int.from_bytes(code[4:],'little')
    need((l&0x707f)==0x5003 and ((l>>7)&31)==15 and ((l>>15)&31)==3 and l>>20==154,'lhu')
    need((b&0x707f)==0x1063 and ((b>>15)&31)==15 and ((b>>20)&31)==18,'bne')
    off=((b>>31&1)<<12)|((b>>7&1)<<11)|((b>>25&63)<<5)|((b>>8&15)<<1)
    if off&4096:off-=8192
    need(0x8a9a+off==0x8abe,'target')
def project(gp,s2,loaded):
    need(0<=loaded<=65535,'halfword')
    return ((gp+154)&MASK,loaded,0x8a9e if loaded==(s2&MASK) else 0x8abe)
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);img=(p.parse_args().root/BIN).read_bytes()
    need(len(img)==76800 and hashlib.sha256(img).hexdigest()==SHA,'APP identity')
    code=img[0x8a96-0x8000:0x8a9e-0x8000];decode(code)
    for v in range(65536):
        for s2 in (v,(v+1)&MASK,v|0x10000):
            address,a5,pc=project((v+0xffffff00)&MASK,s2,v)
            need(address==(v+0xffffff9a)&MASK and a5==v and pc==(0x8a9e if s2==v else 0x8abe),'projection')
    for i in range(len(code)):
        m=bytearray(code);m[i]^=1
        try:decode(m)
        except ValueError:continue
        raise ValueError('mutant accepted')
    print('PASS: 196608 synthetic comparisons and 8 instruction-byte mutations')
    print('LIMIT: assumes sequential arrival and successful halfword read; s2 is then-live full-width value; provider and physical execution unverified')
if __name__=='__main__':main()
