#!/usr/bin/env python3
"""Bounded 0x8a82 provider call boundary, not a complete CPU emulator."""
import argparse,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
MASK=0xffffffff
BYTES=bytes.fromhex('b707040083a7c7139385010882978547630df502')
def need(value,message):
    if not value:raise ValueError(message)
def decode(code):
    need(code==BYTES,'instruction mismatch')
    lui=int.from_bytes(code[0:4],'little');load=int.from_bytes(code[4:8],'little');addi=int.from_bytes(code[8:12],'little');branch=int.from_bytes(code[16:20],'little')
    need((lui&0xfff)==0x7b7 and ((load>>15)&31)==15 and ((load>>7)&31)==15,'slot base')
    slot=(lui&0xfffff000)+((load>>20)&0xfff)
    need((addi&0xfffff)==0x18593 and (addi>>20)==128,'a1 setup')
    off=(((branch>>31)&1)<<12)|(((branch>>7)&1)<<11)|(((branch>>25)&63)<<5)|(((branch>>8)&15)<<1)
    if off&4096:off-=8192
    need((branch&0x1fff07f)==0xf50063 and 0x8a92+off==0x8acc,'return branch')
    return slot
def boundary(gp,handle,target,result):
    return (handle&MASK,(gp+128)&MASK,target&0xfffffffe,0x8a90,0x8acc if (result&MASK)==1 else 0x8a96)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=ROOT);img=(ap.parse_args().root/BIN).read_bytes()
    need(len(img)==76800 and hashlib.sha256(img).hexdigest()==SHA,'APP identity')
    code=img[0x8a82-0x8000:0x8a96-0x8000];need(decode(code)==0x4013c,'slot')
    for value in range(65536):
        for result in (0,1,2,0xffffffff):
            a0,a1,dest,ra,pc=boundary((0xffff8000+value)&MASK,value,(value<<16)|1,result)
            need((a0,a1,dest,ra,pc)==(value,(0xffff8080+value)&MASK,value<<16,0x8a90,0x8acc if result==1 else 0x8a96),'projection')
    for i in range(len(code)):
        m=bytearray(code);m[i]^=1
        try:decode(m)
        except ValueError:continue
        raise ValueError('mutant accepted')
    print('PASS: 262144 synthetic call-boundary projections; 20 byte mutations rejected')
    print('LIMIT: sequential entry, successful slot read and normal provider return are assumed; provider effects, reachability and hardware are not established')
if __name__=='__main__':main()
