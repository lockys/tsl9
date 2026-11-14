#!/usr/bin/env python3
"""Compose index-zero queue-clear projection with subsequent frame restores."""
import argparse,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
s=importlib.util.spec_from_file_location('tail',HERE/'record-counter-clear-tail.py');tail=importlib.util.module_from_spec(s);s.loader.exec_module(tail);m=tail.m
s=importlib.util.spec_from_file_location('queue',HERE/'queue-clear-820c-decoder.py');queue=importlib.util.module_from_spec(s);s.loader.exec_module(queue)
def validate(image):
 queue.validate(image);tail.validate_tail(image)
def clear_zero(gp,mem):
 code={0x820c+i:b for i,b in enumerate(queue.PROVIDER)};ret,events=queue.execute(code,0,gp)
 m.need(ret==0 and len(events)==1 and events[0][0]=='store8','provider event')
 _,addr,value=events[0];mem[addr]=value
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
 print('LIMIT: limited decoder for index 0, successful accesses and preserved gp/sp/s1; synthetic stack alias includes misalignment and does not establish real execution')
if __name__=='__main__':main()
