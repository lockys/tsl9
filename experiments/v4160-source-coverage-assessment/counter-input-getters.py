#!/usr/bin/env python3
"""Resolve local getter inputs to the conditional APP input gate."""
import argparse,hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
WINDOWS=((0x8202,'174500200345f5cd8280'),(0x8440,'03c5c1168280'),(0x81de,'938741059c4303c557000d8905058280'))
def need(v,msg):
    if not v:raise ValueError(msg)
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);root=p.parse_args().root
    data=(root/BIN).read_bytes();need(len(data)==76800 and hashlib.sha256(data).hexdigest()==SHA,'APP identity')
    for pc,h in WINDOWS:
        b=bytes.fromhex(h);need(data[pc-0x8000:pc-0x8000+len(b)]==b,'original getter bytes')
    auipc=int.from_bytes(bytes.fromhex(WINDOWS[0][1])[:4],'little');load=int.from_bytes(bytes.fromhex(WINDOWS[0][1])[4:8],'little');imm=load>>20;imm=imm-4096 if imm&2048 else imm
    need((auipc&127,(auipc>>7)&31,load&127,(load>>12)&7,(load>>7)&31,(load>>15)&31)==(0x17,10,3,4,10,10),'0x8202 operands')
    need((0x8202+(auipc&0xfffff000)+imm)&0xffffffff==0x2000bee1,'0x8202 address')
    word=int.from_bytes(bytes.fromhex(WINDOWS[1][1])[:4],'little')
    need((word&127,(word>>12)&7,(word>>7)&31,(word>>15)&31,word>>20)==(3,4,10,3,364),'0x8440 operands')
    spec=importlib.util.spec_from_file_location('input_gate',Path(__file__).with_name('counter-input-conditions.py'));gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
    for value in range(256):
        flag=(value&3)+1
        need(bool(flag&2)==((value&3) in (1,2)),'getter mask')
        for byte11 in range(256):
            need(gate.input_gate(0x40,byte11,flag)==((value&3) in (1,2) or byte11!=2),'combined gate')
    print('PASS: 65536 synthetic configuration/source-byte pairs; getter 0x8202 reads 0x2000bee1, 0x8440 reads gp+364')
    print('PASS: 0x81de returns (byte[*[gp+84]+5] & 3)+1; bit 1 set exactly for input low bits 1 or 2')
    print('LIMIT: fixed encoding projection; successful reads and stable pointer/GP required; no proof of pointer validity, real values, provider effects, or hardware reachability')
if __name__=='__main__':main()
