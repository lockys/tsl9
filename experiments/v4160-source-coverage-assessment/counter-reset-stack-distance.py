#!/usr/bin/env python3
"""Conditional reset-SP distance to two bounded frame alias sets."""
import argparse
import hashlib
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
spec=importlib.util.spec_from_file_location('stack_alias',Path(__file__).with_name('counter-callee-stack-alias.py'))
alias=importlib.util.module_from_spec(spec);spec.loader.exec_module(alias)
def need(value,msg):
    if not value:raise ValueError(msg)
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);root=p.parse_args().root
    data=(root/BIN).read_bytes();need(len(data)==76800 and hashlib.sha256(data).hexdigest()==SHA,'APP identity')
    def rd(pc,n):return data[pc-0x8000:pc-0x8000+n]
    need(rd(0x186b2,8)==bytes.fromhex('1781ff1f1301e194'),'reset SP instructions')
    au=int.from_bytes(rd(0x186b2,4),'little');ad=int.from_bytes(rd(0x186b6,4),'little')
    need((au&0xfff)==0x117 and (ad&0xfffff)==0x10113,'SP operand encodings')
    imm=ad>>20;imm=imm-4096 if imm&2048 else imm
    reset=(0x186b2+(au&0xfffff000)+imm)&0xffffffff
    need(reset==0x20010000,'reset SP value')
    for pc,code,offsets in alias.FRAMES:
        need(rd(pc,len(code))==code,'callee frame identity')
        eligible={x for x in alias.inverse(offsets) if x%4==0 and x<=reset}
        depths=sorted(reset-x for x in eligible)
        nearest=min(depths)
        need(nearest==(48956 if pc==0x12506 else 48964),'nearest depth')
        for depth in range(0,nearest,4):
            need(not alias.overlapping(reset-depth,offsets),'unexpected alias')
        need(alias.overlapping(reset-nearest,offsets),'witness missing')
        print(f'0x{pc:x}: nearest 4-byte aligned alias is reset SP minus {nearest} (0x{nearest:x})')
    print('PASS: reset SP decoded, all smaller nonnegative 4-byte-aligned depths checked per frame')
    print('LIMIT: assumes direct subtraction from reset SP, preserved stack context and normal execution; no actual maximum stack depth or reachability proven')
if __name__=='__main__':main()
