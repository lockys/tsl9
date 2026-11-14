#!/usr/bin/env python3
"""Conditional input-to-stack composition for the APP counter lookup gate."""
import argparse,hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
WINDOWS=((0xa054,'79714ece06d622d426d24ad0aa89'),(0xa072,'03c499001374040e130404fc13341400'),(0xa08a,'854411e583c4b900f914b3349000'),(0xa0cc,'630e0410638c0410'),(0xa0d4,'b7070400fc473146ce8548008297'))
def need(ok,msg):
    if not ok:raise ValueError(msg)
def input_gate(byte9,byte11,flag):
    return ((byte9&0xe0)==0x40) and (bool(flag&2) or byte11!=2)
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);root=p.parse_args().root
    image=(root/BIN).read_bytes();need(len(image)==76800 and hashlib.sha256(image).hexdigest()==SHA,'APP identity')
    for pc,h in WINDOWS:
        b=bytes.fromhex(h);need(image[pc-0x8000:pc-0x8000+len(b)]==b,'instruction bytes')
    spec=importlib.util.spec_from_file_location('gate',Path(__file__).with_name('counter-lookup-preconditions.py'));gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
    total=0
    for byte9 in range(256):
        for byte11 in range(256):
            for flag in (0,2):
                observed=input_gate(byte9,byte11,flag)
                want=0x40<=byte9<=0x5f and (flag!=0 or byte11!=2)
                need(observed==want,'input gate');total+=observed
    need(total==32*(255+256),'count')
    for packed in range(4096):
        src=bytearray(12);src[5]=packed>>8;src[6]=packed&255;src[9]=0x40;src[11]=0
        stack=bytearray(48);stack[4:16]=src
        word=int.from_bytes(stack[8:12],'little');byte10=stack[10]
        actual=gate.project(word,byte10,0)[0]==0xa146
        need(actual==(1961<=packed<=2139),'source/stack relation')
    print(f'PASS: 131072 input/flag cases, {total} pass local gates; all 4096 packed source values checked')
    print('LIMIT: assumes normal earlier getters, 0x8202 nonzero, 0x8440 nonzero, copy provider acts as 12-byte copy, successful accesses and no interference; no provider identity or reachability proof')
if __name__=='__main__':main()
