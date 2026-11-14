#!/usr/bin/env python3
"""Bounded post-provider counter decision from original 0x107d8 instructions.

Inputs are values at the post-call boundary, not a complete function or ABI.
Assumes the shown accesses succeed; no concurrent writes or hardware effects.
"""
import argparse,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
# 0x107d8..0x107ee plus the two out-of-line stores.
WINDOWS=((0x107d8,'05cd83470400b245850793f7f70f63f9b7002300f400'),(0x107f8,'23000400'),(0x10810,'23000400'))
def need(c,msg):
 if not c:raise ValueError(msg)
def validate(image):
 need(len(image)==76800 and hashlib.sha256(image).hexdigest()==SHA,'identity')
 for pc,expected in WINDOWS:need(image[pc-0x8000:pc-0x8000+len(bytes.fromhex(expected))]==bytes.fromhex(expected),f'instructions at {pc:x}')
def project(ret,old,threshold):
 need(0<=ret<=0xffffffff and 0<=old<=255 and 0<=threshold<=0xffffffff,'input width')
 if ret==0:return 0,0x107ee
 new=(old+1)&255
 if threshold<=new:return 0,0x107fc
 return new,0x107ee
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);validate((p.parse_args().root/BIN).read_bytes())
 count=0
 for old in range(256):
  for limit in range(256):
   for ret in (0,1):
    value,pc=project(ret,old,limit);next_=(old+1)&255
    need((value,pc)==((0,0x107ee) if not ret else ((0,0x107fc) if next_>=limit else (next_,0x107ee))),'decision');count+=1
  for limit in (256,0xffff,0x10000,0xffffffff):
   need(project(1,old,limit)==((old+1)&255,0x107ee),'full-width threshold')
 print(f'PASS: {count} byte threshold/return decisions; 1024 full-width limits')
 print('LIMIT: hand-written fixed-encoding projection and arithmetic enumeration, not independent instruction execution; stops before clear call; provider state, accesses, aliasing, interrupts and hardware not established')
if __name__=='__main__':main()
