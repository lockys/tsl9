#!/usr/bin/env python3
"""Conditional queue-record witnesses for selector 0x370 and APP lookup gates."""
import argparse,hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
WINDOWS=((0x12d8a,'2800ef10307a'),(0x14f18,'13070037638ae73a'),(0x152d0,'22852244b24041016f40dfd7'))
def need(v,msg):
    if not v:raise ValueError(msg)
def load(filename,name):
    spec=importlib.util.spec_from_file_location(name,Path(__file__).with_name(filename));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);root=p.parse_args().root
    image=(root/BIN).read_bytes();need(len(image)==76800 and hashlib.sha256(image).hexdigest()==SHA,'APP identity')
    for pc,h in WINDOWS:
        b=bytes.fromhex(h);need(image[pc-0x8000:pc-0x8000+len(b)]==b,'original bytes')
    gate=load('counter-lookup-preconditions.py','gate');check=load('counter-input-checksum-witness.py','check');inp=load('counter-input-conditions.py','inp')
    for pc,target in ((0x12d8c,0x14d2e),(0x152d8,0xa054)):
        need(gate.jal(pc,int.from_bytes(image[pc-0x8000:pc-0x8000+4],'little'))==target,'JAL target')
    need(gate.branch(0x14f1c,int.from_bytes(image[0x14f1c-0x8000:0x14f20-0x8000],'little'))==0x152d0,'selector branch')
    count=0
    for packed in range(1961,2140):
        for value in range(256):
            src=bytearray(12);src[0]=0x70;src[1]=3;src[2]=8;src[5]=packed>>8;src[6]=packed&255;src[9]=0x40;src[10]=value
            src[3]=(value-check.checksum(src))&255
            need(int.from_bytes(src[:2],'little')==0x370 and check.checksum(src)==src[10],'record header/checksum')
            need(inp.input_gate(src[9],src[11],0),'input gate')
            stack=bytearray(48);stack[4:16]=src
            need(gate.project(int.from_bytes(stack[8:12],'little'),stack[10],0)[0]==0xa146,'lookup gate')
            count+=1
    print(f'PASS: {count} synthetic 0x0370 records, length byte 8, satisfy checksum and conditional input/lookup gates')
    print('LIMIT: dispatch selector 1 and guards, queue record persistence, copy semantics, normal calls and stable nonaliasing accesses are assumed; not continuous CPU, producer reachability or hardware')
if __name__=='__main__':main()
