#!/usr/bin/env python3
"""Compose index-zero queue-clear projection with subsequent frame restores."""
import argparse,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
s=importlib.util.spec_from_file_location('tail',HERE/'record-counter-clear-tail.py');tail=importlib.util.module_from_spec(s);s.loader.exec_module(tail);m=tail.m
PROVIDER=bytes.fromhex('894763e7a7009387010caa97a38007008280')
def validate(image):
 m.validate(image);tail.validate_tail(image);m.need(image[0x20c:0x21e]==PROVIDER,'queue-clear bytes')
def clear_zero(gp,mem):mem[(gp+193)&MASK]=0
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();validate(image)
 gp=0x20004000;dst=gp+193;count=0;changes=0
 for offset in (20,24,28):
  for byte in range(4):
   sp=(dst-offset-byte)&MASK
   for value in range(256):
    mem={}
    for off in (20,24,28):
     for i in range(4):mem[(sp+off+i)&MASK]=0x55
    mem[dst]=value;before=tail.after_provider(sp,0x12345678,mem);clear_zero(gp,mem);after=tail.after_provider(sp,0x12345678,mem)
    field={20:'s1',24:'s0',28:'ra'}[offset]
    m.need(after[field]==(before[field]&~(255<<(8*byte))),'cleared byte')
    for other in {'s1','s0','ra'}-{field}:m.need(after[other]==before[other],'unrelated saved word')
    m.need(after['a0']==0x12345678 and after['target']==0x1074c,'forwarded s1');changes+=before[field]!=after[field];count+=1
 print(f'PASS: {count} shared-memory provider/tail projections; {changes} saved-word changes')
 print('LIMIT: provider summarized for index 0, successful accesses and preserved gp/sp/s1; synthetic stack alias includes misalignment and does not establish real execution')
if __name__=='__main__':main()
