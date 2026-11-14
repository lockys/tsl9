#!/usr/bin/env python3
"""Bounded TX copy-step projection; successful byte access, not hardware."""
import argparse,hashlib,random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];MASK=0xffffffff
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
WINDOWS=((0x8b0a,'13950501418163618504'),(0x8b52,'3385b400034505003388b70085052a97a302a8001377f70f45b7'))
def need(v,m):
    if not v:raise ValueError(m)
def step(index,length,src,dest,checksum,memory):
    if (index&0xffff)>=length:return 0x8b14,index,checksum,[]
    source=(src+index)&MASK;target=(dest+index+5)&MASK
    value=memory[source];memory[target]=value
    return 0x8b0a,(index+1)&MASK,(checksum+value)&255,[('read',source,value),('write',target,value)]
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);args=p.parse_args()
    raw=(args.root/BIN).read_bytes();need(len(raw)==76800 and hashlib.sha256(raw).hexdigest()==SHA,'firmware identity')
    for pc,h in WINDOWS:
        b=bytes.fromhex(h);need(raw[pc-0x8000:pc-0x8000+len(b)]==b,'instruction bytes')
    rng=random.Random(0x8b0a)
    for index in range(65536):
        high=rng.getrandbits(16)<<16;index|=high;src=0x12345678;dest=src-4;value=index&255
        memory={(src+index)&MASK:value};a=step(index,(index&0xffff)+1,src,dest,255,memory)
        need(a[0]==0x8b0a and a[1]==(index+1)&MASK and a[2]==(255+value)&255 and a[3][1][1]==(src+index+1)&MASK,'copy')
        need(step(index,index&0xffff,src,dest,17,{})==(0x8b14,index,17,[]),'exit')
    memory={0x1000:42,0x1001:99}
    step(0,2,0x1000,0xffc,0,memory);result=step(1,2,0x1000,0xffc,0,memory)
    need(result[3][0][2]==42,'forward alias')
    print('PASS: 65536 copy and exit pairs, full-width indices and forward-alias witness')
    print('LIMIT: fixed bytes and manual projection; no instruction execution, trap, concurrency, ABI or hardware proof')
if __name__=='__main__':main()
