#!/usr/bin/env python3
"""Conditional descriptor-write/tail shared-memory witnesses; not a CPU emulator."""
import argparse,hashlib,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];M=0xffffffff
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,HERE/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
meta=load('metadata','tx-finish-metadata.py');tail=load('tail','tx-finish-tail.py');entry=tail.entry
def put(mem,address,width,value):
    for i in range(width):mem[(address+i)&M]=(value>>(8*i))&255
def apply(mem,events):
    for addr,width,val in events:put(mem,addr,width,val)
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/entry.BIN).read_bytes()
    entry.need(len(image)==76800 and hashlib.sha256(image).hexdigest()==entry.SHA,'identity');meta.window(image[0xb1a:0xb3a]);tail.verify(image[0xb3a:0xb52])
    # Synthetic descriptor base 0x4004e: first SH overwrites low half of slot.
    for n in range(65536):
        mem={};put(mem,0x40050,4,0x12345678);ev=meta.events(0,0x4004e,n);apply(mem,ev)
        target,*_=tail.project(mem,0,0,0,0)
        entry.need(target==((n+6)&0xfffe),'target slot alias')
    # Descriptor first SH overlaps restored s0; stack and descriptor share bytes.
    for n in range(65536):
        mem={};sp=0x20004000;put(mem,sp+24,4,0x12345678);apply(mem,meta.events(0,sp+22,n))
        _,_,_,_,_,restored,_=tail.project(mem,0,0,sp,0)
        entry.need(restored==((n+6)&0xffff),'saved s0 alias')
    print('PASS: 65536 provider-slot and 65536 saved-s0 synthetic alias cases')
    print('LIMIT: fixed-instruction projections composed at boundary; assumes successful loads/stores, no interrupts; synthetic aliases not established reachable or hardware')
if __name__=='__main__':main()
