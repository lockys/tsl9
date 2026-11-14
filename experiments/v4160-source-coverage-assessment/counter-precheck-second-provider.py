#!/usr/bin/env python3
"""Conditional second provider call projection at 0x8a9e, not CPU execution."""
import argparse,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
CODE=bytes.fromhex('c167f917630ef900b707040083a7c713938501084a85829785470546630af500')
MASK=0xffffffff
def need(v,msg):
    if not v:raise ValueError(msg)
def check(code):
    need(code==CODE,'instruction mismatch')
    for pos,pc,target in ((4,0x8aa2,0x8abe),(28,0x8aba,0x8ace)):
        b=int.from_bytes(code[pos:pos+4],'little');off=((b>>31&1)<<12)|((b>>7&1)<<11)|((b>>25&63)<<5)|((b>>8&15)<<1)
        if off&4096:off-=8192
        need((b&0x707f)==0x63 and pc+off==target,'branch')
def project(gp,s2,target,result):
    if s2==0xfffe:return (None,0x8abe,None)
    return ((s2,(gp+128)&MASK,target&0xfffffffe,0x8ab6),0x8ace if result==1 else 0x8abe,1)
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/BIN).read_bytes()
    need(len(image)==76800 and hashlib.sha256(image).hexdigest()==SHA,'APP identity');code=image[0xa9e:0xabe];check(code)
    for h in range(65536):
        for result in (0,1,2,0xffffffff):
            c,pc,a2=project(0xfffffff0,h,(h<<16)|1,result)
            if h==0xfffe:need((c,pc,a2)==(None,0x8abe,None),'sentinel')
            else:need(c==(h,0x70,h<<16,0x8ab6) and pc==(0x8ace if result==1 else 0x8abe) and a2==1,'call')
    for i in range(len(code)):
        m=bytearray(code);m[i]^=1
        try:check(m)
        except ValueError:continue
        raise ValueError('mutant accepted')
    print('PASS: 262144 synthetic second-call cases and 32 instruction-byte mutations')
    print('LIMIT: sequential entry, successful slot read and normal return assumed; slot can differ from first call; provider effects, reachability and physical behavior unverified')
if __name__=='__main__':main()
