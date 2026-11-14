#!/usr/bin/env python3
"""Checksum store before stack RA reload: synthetic shared-memory alias witness."""
import argparse,hashlib,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
s=importlib.util.spec_from_file_location('store',HERE/'tx-checksum-store.py');store=importlib.util.module_from_spec(s);s.loader.exec_module(store)
# 0x8b1a..0x8b26 has no store or branch; 0x8b26 is c.lwsp ra,28(sp).
BETWEEN=bytes.fromhex('93076042b307f60219040a06');LOAD=bytes.fromhex('f240')
def read32(mem,a):return sum(mem.get((a+i)&MASK,0)<<(8*i) for i in range(4))
def run(sp,a5,n,value):
    mem={((sp+28+i)&MASK):b for i,b in enumerate((0x12,0x34,0x56,0x78))}
    before=read32(mem,(sp+28)&MASK);addr,_,v=store.project(a5,n,value);mem[addr]=v
    return before,read32(mem,(sp+28)&MASK),addr

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);root=p.parse_args().root;img=(root/store.BIN).read_bytes()
    store.need(len(img)==76800 and hashlib.sha256(img).hexdigest()==store.SHA,'identity');store.decode(img[0xb14:0xb1a]);store.need(img[0xb1a:0xb26]==BETWEEN and img[0xb26:0xb28]==LOAD,'instructions')
    for sp in (0,0x20004000,0xffffffe0,0xffffffff):
        for byte in range(256):
            for i in range(5):
                addr=(sp+28+i)&MASK;a5=(addr-5-7)&MASK;before,after,actual=run(sp,a5,7,byte)
                expect=(before&~(255<<(8*i)))|(byte<<(8*i)) if i<4 else before
                store.need(actual==addr and after==expect,'alias projection')
    print('PASS: 5120 synthetic byte/offset/wrap cases; four saved-RA alias bytes and one disjoint control')
    print('LIMIT: assumes successful 32-bit stack load, byte-addressed little-endian memory and no external effects; includes unaligned synthetic SP which may trap; not demonstrated reachable or hardware')
if __name__=='__main__':main()
