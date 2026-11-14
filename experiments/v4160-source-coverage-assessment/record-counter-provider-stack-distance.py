#!/usr/bin/env python3
"""Conditional distances from reset stack to queue-clear saved-word aliases."""
import argparse,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
provider=load('provider','record-counter-clear-provider-alias.py');bound=load('bound','record-counter-caller-stack-bound.py');m=provider.m

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();provider.validate(image);bound.validate_windows(image)
 # These values come from reset AUIPC/ADDI byte windows verified above.
 gp=0x20004000;reset=0x20010000;addr=gp+193
 for offset,name in ((20,'s1'),(24,'s0'),(28,'ra')):
  candidates={(addr-offset-byte)&MASK for byte in range(4)};aligned=[sp for sp in candidates if sp%4==0 and sp<=reset]
  m.need(len(aligned)==1,'aligned witness');sp=aligned[0];depth=reset-sp
  for d in range(0,depth,4):m.need(addr not in range(reset-d+offset,reset-d+offset+4),'earlier alias')
  mem={}
  for off in (20,24,28):
   for i in range(4):mem[sp+off+i]=0x55
  before=provider.tail.after_provider(sp,0x1234,mem);provider.clear_zero(gp,mem);after=provider.tail.after_provider(sp,0x1234,mem)
  m.need(before[name]!=after[name],'witness');print(f'{name}: frame SP=0x{sp:08x}, reset depth={depth} bytes, saved byte={(addr-sp-offset)}')
 print('PASS: all smaller nonnegative 4-byte-aligned depths excluded independently for each saved word')
 print('LIMIT: assumes reset gp/SP remain applicable, normal provider call and downward stack; no actual maximum depth or reachability proof')
if __name__=='__main__':main()
