#!/usr/bin/env python3
"""Decode the pinned RV32 store and project one successful ordinary-RAM write.

No CPU, alignment, live GP, callback reachability, or hardware is modeled.
"""
import hashlib
from pathlib import Path
BIN=Path(__file__).resolve().parents[2]/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
EXPECTED=bytes.fromhex('a387010a8280')
MASK=0xffffffff

def decode(code):
 if len(code)!=6:raise ValueError('leaf length')
 word=int.from_bytes(code[:4],'little')
 imm=((word>>25)<<5)|((word>>7)&31)
 if imm&0x800:imm-=0x1000
 if (word&127,(word>>12)&7,(word>>15)&31,(word>>20)&31,imm,code[4:])!=(0x23,0,3,0,175,b'\x82\x80'):
  raise ValueError('unsupported instruction fields')
 return imm

def project(code,gp,memory):
 if type(gp) is not int or not 0<=gp<=MASK:raise ValueError('GP range')
 offset=decode(code);addr=(gp+offset)&MASK
 if addr not in memory:raise ValueError('unmapped byte')
 out=dict(memory);out[addr]=0
 return out,('write8',addr,0)

def main():
 raw=BIN.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('image identity')
 code=raw[0x1f74:0x1f7a]
 if code!=EXPECTED:raise ValueError('leaf identity')
 count=0
 for gp in (0,0x20004000,0xffffff50,0xffffffff):
  addr=(gp+175)&MASK
  for old in range(256):
   memory={addr:old,(addr+1)&MASK:0x5a};out,event=project(code,gp,memory)
   if out[addr]!=0 or out[(addr+1)&MASK]!=0x5a or event!=('write8',addr,0):raise ValueError('bad projection')
   count+=1
 print(f'PASS: {count} single-byte projections; RV32 sb zero,175(gp); ret')
 print('LIMIT: projected successful ordinary RAM only; not a CPU or live GP proof')
if __name__=='__main__':main()
