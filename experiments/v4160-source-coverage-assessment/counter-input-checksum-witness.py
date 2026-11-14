#!/usr/bin/env python3
"""Construct conditional source bytes satisfying APP local checksum and range gates."""
import argparse,hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
WINDOWS=((0x1069e,'41119d4522c406c62a84efe08fe58347a400b24022443385a7401335150041018280'),(0xed00,'035705000346250093578700ba9793f7f70f01479376f70f63e4c6003e8582806389d500b306e50083c63600b69793f7f70f0507c5b7'))
def need(ok,msg):
    if not ok:raise ValueError(msg)
def checksum(src):
    # For the a1=7 call, index seven (source byte 10) is not read by 0xed00.
    n=src[2];need(len(src)>=max(3,3+n),'source length')
    return (src[0]+src[1]+sum(src[3+i] for i in range(n) if i!=7))&255
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);root=p.parse_args().root
    image=(root/BIN).read_bytes();need(len(image)==76800 and hashlib.sha256(image).hexdigest()==SHA,'APP identity')
    for pc,h in WINDOWS:
        b=bytes.fromhex(h);need(image[pc-0x8000:pc-0x8000+len(b)]==b,'original bytes')
    spec=importlib.util.spec_from_file_location('input_gate',Path(__file__).with_name('counter-input-conditions.py'));g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
    spec=importlib.util.spec_from_file_location('lookup_gate',Path(__file__).with_name('counter-lookup-preconditions.py'));q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
    count=0
    for packed in range(1961,2140):
        for check in range(256):
            src=bytearray(12);src[2]=8;src[5]=packed>>8;src[6]=packed&255;src[9]=0x40;src[10]=check
            src[3]=(check-checksum(src))&255
            need(checksum(src)==src[10],'checksum')
            need(g.input_gate(src[9],src[11],0),'input gate')
            stack=bytearray(48);stack[4:16]=src
            need(q.project(int.from_bytes(stack[8:12],'little'),stack[10],0)[0]==0xa146,'range gate')
            count+=1
    print(f'PASS: {count} synthetic sources satisfy local checksum and input/range gates (179 packed values x 256 checksum bytes)')
    print('LIMIT: fixed-instruction semantic projection, not continuous CPU execution; assumes aligned successful stable reads, normal calls, nonoverlapping 12-byte copy and caller-supplied byte getter; real provider/input/hardware unknown')
if __name__=='__main__':main()
