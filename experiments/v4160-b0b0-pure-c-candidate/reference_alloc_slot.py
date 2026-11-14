#!/usr/bin/env python3
"""Inspect conditional mapped entry for two reference resident allocator slots."""
import argparse
import hashlib
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from reference_free_slot import CASES, ROOT

PREFIX=bytes.fromhex('411126c24ac0b744024006c622c403a9c42023a604200f10000009e923a62421b240224492440249410182802a842105bd654205c18d4181c93b')
SOURCES=(0x404a6,0x404e6)


def need(ok,message):
    if not ok: raise ValueError(message)


def check(data,digest,source):
    need(hashlib.sha256(data).hexdigest()==digest,'reference hash mismatch')
    need(int.from_bytes(data[0x70:0x74],'little')==0x20000236,'slot differs')
    need(data[source-0x40000:source-0x40000+len(PREFIX)]==PREFIX,'mapped prefix differs')


def projection(a0,incoming):
    if a0==0:
        return ('return',incoming)
    return ('helper-20000040',(a0+8)&0xffff,0xf000|a0)


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT)
    root=p.parse_args().root
    for (path,digest,_,_),source in zip(CASES,SOURCES):
        file=root/path
        if not file.is_file(): raise SystemExit(f'SKIP: missing reference carrier {path}')
        data=file.read_bytes();check(data,digest,source)
        for i in list(range(0x70,0x74))+list(range(source-0x40000,source-0x40000+len(PREFIX))):
            changed=bytearray(data);changed[i]^=1
            try:check(changed,digest,source)
            except ValueError:continue
            raise ValueError('mutated reference accepted')
        print(f'PASS: slot 0x40070 -> 0x20000236; {len(PREFIX)}-byte candidate prefix at flash {source:#x}; {len(PREFIX)+4} mutations rejected by full hash')
    for incoming in range(65536):
        need(projection(12,incoming)==('helper-20000040',20,0xf00c),'helper args')
        need(projection(0,incoming)==('return',incoming),'zero a1')
    print('PASS: 65536 incoming a1 samples: candidate f7 zero-object helper args = (20, 0xf00c)')
    print('LIMIT: conditional flash-to-RAM copy, memory and successful access assumed; no CPU, installed resident, helper or hardware execution')


if __name__=='__main__':main()
