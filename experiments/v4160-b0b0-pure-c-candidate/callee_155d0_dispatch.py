#!/usr/bin/env python3
"""Bounded 0x1560e dispatch and a1 provenance; no provider or indirect target execution."""
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BIN=ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
START=0x1560e
EXPECTED=bytes.fromhex('1309f5ff1377f90f9d472a8463ebe70081465146814517050000130565f0ef309faf1379f90f9307c00f63ea2715175700001307870b0a093a9983270900ba978287')


def need(ok,message):
    if not ok:
        raise ValueError(message)


def branch(data,pc,funct,rs1,rs2):
    w=int.from_bytes(data,'little')
    need(w&0x7f==0x63 and (w>>12)&7==funct and (w>>15)&31==rs1 and (w>>20)&31==rs2,'unexpected branch')
    imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    return pc+imm-(0x2000 if imm&0x1000 else 0)


def jal(data,pc):
    w=int.from_bytes(data,'little')
    need(w&0x7f==0x6f and (w>>7)&31==1,'unexpected call')
    imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    return pc+imm-(0x200000 if imm&0x100000 else 0)


def check(data):
    chunk=data[START-0x8000:START-0x8000+len(EXPECTED)]
    need(chunk==EXPECTED,'dispatch window mismatch')
    at=lambda pc:data[pc-0x8000:pc-0x8000+4]
    need(branch(at(0x1561a),0x1561a,6,15,14)==0x15630,'first branch target')
    need(branch(at(0x15638),0x15638,6,15,18)==0x1578c,'second branch target')
    need(jal(at(0x1562c),0x1562c)==0x9124,'scheduler call target')


def dispatch(arg,a1):
    x=(arg-1)&255
    if x<=7:
        return 'call-9124',0
    if x>252:
        return 'return-1578c',a1
    return 'table-read-15648',a1


def main():
    data=BIN.read_bytes()
    need(len(data)==76800 and hashlib.sha256(data).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','BIN identity mismatch')
    check(data)
    counts={'call-9124':0,'return-1578c':0,'table-read-15648':0}
    for arg in range(256):
        for sample in range(256):
            old=dispatch(arg,sample)
            new=dispatch(arg,0x2000c000)
            counts[old[0]]+=1
            need(old[0]==new[0],'a1 affects selection')
            if old[0]=='call-9124':
                need(old[1]==new[1]==0,'scheduler a1')
            else:
                need(old[1]==sample and new[1]==0x2000c000,'a1 preserved')
    need(counts=={'call-9124':2048,'return-1578c':768,'table-read-15648':62720},'partition mismatch')
    for i in range(len(EXPECTED)):
        changed=bytearray(data);changed[START-0x8000+i]^=1
        try:
            check(changed)
        except ValueError:
            continue
        raise ValueError('mutated instruction accepted')
    print(f'PASS: 65536 conditional arg/a1 projections: {counts}')
    print(f'PASS: {len(EXPECTED)} local instruction-byte mutations rejected')
    print('LIMIT: stop before provider call or table read; prior branches, memory aliasing, runtime and other callers are not proved')


if __name__=='__main__':
    main()
