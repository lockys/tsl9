#!/usr/bin/env python3
"""Conditional projection of original TX finish metadata writes, not CPU emulation."""
import argparse,hashlib,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];M=0xffffffff
spec=importlib.util.spec_from_file_location('entry',HERE/'tx-entry-length-guard.py');entry=importlib.util.module_from_spec(spec);spec.loader.exec_module(entry)
# Exact 0x8b1a..0x8b3a, including intervening stack loads and li a1.
RAW=bytes.fromhex('93076042b307f60219040a06f240d2444249b2498545b6972391870023920700')
def window(b):entry.need(b==RAW,'finish instruction window')
def events(a2,a3,s0):
    base=(a3+((a2*1062)&M))&M
    return (((base+2)&M,2,(s0+6)&0xffff),((base+4)&M,2,0))
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/entry.BIN).read_bytes()
    entry.need(len(image)==76800 and hashlib.sha256(image).hexdigest()==entry.SHA,'identity');raw=image[0xb1a:0xb3a];window(raw)
    for i in range(len(raw)):
        b=bytearray(raw);b[i]^=1
        try:window(b)
        except ValueError:continue
        raise ValueError('mutation accepted')
    for n in range(65536):
        for a2,a3 in ((0,0),(1,0x2000b18c),(0xffffffff,0xffffffff),(0x80000000,0xfffffff0)):
            e=events(a2,a3,n);base=(a3+a2*1062)&M
            entry.need(e==(((base+2)&M,2,(n+6)%65536),((base+4)&M,2,0)),'projection')
    print(f'PASS: 262144 synthetic metadata projections; {len(raw)} mutated instruction bytes rejected')
    print('LIMIT: fixed encoding projection, successful intervening stack reads and stores assumed; no atomicity, physical memory, provider or reachability proof')
if __name__=='__main__':main()
