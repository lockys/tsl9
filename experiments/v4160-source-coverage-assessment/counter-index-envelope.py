#!/usr/bin/env python3
"""Classify syntactic u8 counter reads relative to known data and APP image."""
import argparse
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BASE=0x8000
TABLE=0x1ab48
KNOWN=(0x0096,0x00b4,0xff6a,0xff4c)

def need(ok,reason):
    if not ok:raise ValueError(reason)

def classify(image):
    need(len(image)==76800 and hashlib.sha256(image).hexdigest()==SHA,'APP identity')
    code=image[0xa146-BASE:0xa15c-BASE]
    need(code.hex()=='83c7010b13971700971701009387a79fba9783d70700','counter lookup encoding')
    lbu=int.from_bytes(code[:4],'little');slli=int.from_bytes(code[4:8],'little')
    auipc=int.from_bytes(code[8:12],'little');addi=int.from_bytes(code[12:16],'little')
    need((lbu&127,(lbu>>12)&7,(lbu>>7)&31,(lbu>>15)&31,lbu>>20)==(3,4,15,3,176),'counter lbu')
    need((slli&127,(slli>>12)&7,(slli>>7)&31,(slli>>15)&31,slli>>20)==(19,1,14,15,1),'index shift')
    imm=(addi>>20)&0xfff;imm=imm-4096 if imm&0x800 else imm
    need((auipc&127,(auipc>>7)&31,addi&127,(addi>>7)&31,(addi>>15)&31)==(23,15,19,15,15),'table base registers')
    need((0xa14e+(auipc&0xfffff000)+imm)&0xffffffff==TABLE,'table base')
    need(code[16:18]==bytes.fromhex('ba97') and code[18:22]==bytes.fromhex('83d70700'),'index add and halfword load')
    image_end=BASE+len(image)
    off=TABLE-BASE
    need(tuple(int.from_bytes(image[off+2*i:off+2*i+2],'little') for i in range(4))==KNOWN,'known cells')
    groups={'known':[], 'other_in_image':[], 'outside_image':[]}
    for i in range(256):
        addr=TABLE+2*i
        name='known' if i<4 else ('other_in_image' if BASE<=addr and addr+2<=image_end else 'outside_image')
        groups[name].append((i,addr))
    return groups

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=ROOT)
    image=(parser.parse_args().root/BIN).read_bytes();g=classify(image)
    need([len(g[k]) for k in ('known','other_in_image','outside_image')]==[4,88,164],'unexpected partition')
    need(g['outside_image'][0]==(92,0x1ac00) and g['outside_image'][-1]==(255,0x1ad46),'outside bounds')
    altered=bytearray(image);altered[TABLE-BASE]^=1
    try:classify(altered)
    except ValueError:pass
    else:raise ValueError('mutated image accepted')
    print('PASS: 256 byte indices: 4 known cells, 88 other image halfwords, 164 beyond supplied image; 328 outside bytes; mutated image rejected')
    print('LIMIT: syntactic envelope only; no proof index reaches these values, no claim physical memory read fails or full-table extent')

if __name__=='__main__':main()
