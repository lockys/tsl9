#!/usr/bin/env python3
"""Resolve the two original APP byte getters relevant to lookup bypass."""
import argparse,hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
WINDOWS=((0x81ee,'17450020034575ce8280',0x2000bed5),(0x81f8,'17450020034525cf8280',0x2000beea))
def need(ok,msg):
    if not ok:raise ValueError(msg)
def getter_address(pc,raw):
    need(len(raw)==10 and raw[8:]==b'\x82\x80','ret')
    a=int.from_bytes(raw[:4],'little');b=int.from_bytes(raw[4:8],'little')
    need((a&127,(a>>7)&31)==(0x17,10),'auipc a0')
    need((b&127,(b>>7)&31,(b>>12)&7,(b>>15)&31)==(3,10,4,10),'lbu a0,imm(a0)')
    imm=b>>20;imm=imm-4096 if imm&2048 else imm
    return (pc+(a&0xfffff000)+imm)&0xffffffff
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=ROOT);root=parser.parse_args().root
    image=(root/BIN).read_bytes();need(len(image)==76800 and hashlib.sha256(image).hexdigest()==SHA,'APP identity')
    for pc,h,address in WINDOWS:
        raw=image[pc-0x8000:pc-0x8000+10];need(raw==bytes.fromhex(h),'getter bytes')
        need(getter_address(pc,raw)==address,'getter address')
        need(address!=0x200040b0,'getter overlaps counter')
    spec=importlib.util.spec_from_file_location('gate',Path(__file__).with_name('counter-lookup-preconditions.py'));gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
    for byte in range(256):
        pc,_=gate.project(0x700,0xa9,byte)
        need(pc==(0xa168 if byte==1 else 0xa1fc if byte==2 else 0xa146),'getter/guard')
    print('PASS: fixed bytes resolve 0x81ee -> LBU 0x2000bed5 and 0x81f8 -> LBU 0x2000beea; all 256 getter results checked')
    print('LIMIT: conditional successful loads and normal returns, shared state stable; no global writer, live addresses/values, caller reachability or hardware proof')
if __name__=='__main__':main()
