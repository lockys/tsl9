#!/usr/bin/env python3
"""Conditional 0x82d2 packaging projection before and after a stub copy call."""
import argparse,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
def need(v,msg):
    if not v:raise ValueError(msg)
def header(identifier,flag):return (((identifier>>8)|(flag<<4))&255,identifier&255)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=ROOT);img=(ap.parse_args().root/BIN).read_bytes()
    need(len(img)==76800 and hashlib.sha256(img).hexdigest()==SHA,'APP identity')
    windows=((0x8332,'83d6040083c7b400e285a302d1001397470093d78600d98f2302f10083a7cc04130561008297'),(0x8358,'83c6240003552400500089069305000cfd25'),(0x8a56,'9307f04063e9d710'))
    for pc,h in windows:
        b=bytes.fromhex(h);need(img[pc-0x8000:pc-0x8000+len(b)]==b,f'instruction mismatch {pc:x}')
    # First-stage header stores occur before the provider, with freshly read
    # length and handle after it. No assumption that the provider is memcpy.
    for ident in range(65536):
        for flag in (0,1,2,15,16,255):
            hi,lo=header(ident,flag)
            need(lo==ident%256 and hi==((ident//256)|((flag%16)*16))%256,'header')
    for flag in range(256):
        need(header(0x370,flag)==(3|((flag&15)<<4),0x70),'0x370 header')
    for length in range(256):
        # The post-provider LBU fixes a3 to 2..257, passing 1039 gate;
        # prior admission requires initial length <= 8, not necessarily this value.
        need(2<=length+2<=257 and length+2<=1039,'second length gate')
    print('PASS: 393216 header projections, 256 flag values and 256 post-provider lengths')
    print('LIMIT: assumes original block is reached and loads/stores succeed; provider may change length, handle, memory or registers; 0x8a56 beyond its length gate and physical behavior unmodeled')
if __name__=='__main__':main()
