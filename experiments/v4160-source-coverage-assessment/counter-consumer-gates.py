#!/usr/bin/env python3
"""Conditional queue consumer gates and dispatcher selector for ID 0x370."""
import argparse, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
def need(value,message):
    if not value:raise ValueError(message)
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/BIN).read_bytes()
    need(len(image)==76800 and hashlib.sha256(image).hexdigest()==SHA,'APP identity')
    windows=((0x12cae,'2800ef502fe20ded83578100639f470b'),(0x12d78,'83a70b0083c74700a18bb5f7ef506fc23dd12800ef10307a'),(0x81aa,'03c5710a8280'),(0x829e,'17450020034575d18280'),(0x14d2e,'411122c406c62a84ef308fd6994763efa77417670000130787970a053a951c41ba978287'),(0x14d5e,'83570400'))
    for pc,h in windows:
        b=bytes.fromhex(h);need(image[pc-0x8000:pc-0x8000+len(b)]==b,f'instruction mismatch {pc:x}')
    base=0x14d40+0x6000-1672;need(base==0x1a6b8,'table base')
    raw=int.from_bytes(image[base+4-0x8000:base+8-0x8000],'little',signed=True)
    need((base+raw)&0xffffffff==0x14d5e,'selector 1 destination')
    # AUIPC+LBU getter at 0x829e, not an assumed static selector.
    need((0x829e+0x20004000-745)&0xffffffff==0x2000bfb5,'selector location')
    accepted=0
    for flags in range(256):
        for enabled in range(256):
            # 0x82d2 must return 0 and reads/stored fields must remain stable.
            call=not(flags&8) and enabled!=0
            if call:accepted+=1
            need(call==(flags&8==0 and enabled>0),'gate classification')
    need(accepted==128*255,'accepted count')
    print(f'PASS: 65536 flag/enable pairs, {accepted} conditionally call dispatcher; selector byte 1 reaches ID decision tree')
    print('LIMIT: assumes 0x82d2 returns zero, getter/call preservation, successful stable nonaliasing reads and no interrupts; not full dispatcher execution or hardware reachability')
if __name__=='__main__':main()
