#!/usr/bin/env python3
"""Conditional reset-SP distances for b0fc local stores and saved words.

This enumerates addresses, not reachable program states. Assumes live GP equals
reset GP, frame SP descends from reset SP by a nonnegative 4-byte-aligned depth,
and address arithmetic is 32-bit. No actual stack-depth bound is asserted.
"""
import argparse,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
m=load('m','record-counter-107d8.py');body=load('body','callback-provider-b0fc-decoder.py')
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();m.validate(image);body.model.validate_local(image)
 gp=0x20004000;reset_sp=0x20010000;base=gp+192;_,events=body.execute(0xa5,base,0x43c4e)
 writes=set()
 for e in events:
  if e[0] in ('store8','store16'):
   writes.update((e[1]+i)&0xffffffff for i in range(1 if e[0]=='store8' else 2))
 m.need(writes==set(range(base,base+4)),'unexpected store range')
 for name,offset in [('s1',4),('s0',8),('ra',12)]:
  candidates=[]
  for depth in range(0,reset_sp-gp+64,4):
   sp=reset_sp-depth;word=set(range(sp+offset,sp+offset+4))
   if writes & word:candidates.append((depth,sp))
  m.need(len(candidates)==1,'unexpected aligned candidates')
  depth,sp=candidates[0];m.need(sp+offset==base,'unexpected aligned intersection')
  print(f'{name}: frame SP=0x{sp:08x}, reset-to-frame depth={depth} bytes')
 print('PASS: pinned local bytes and exhaustive aligned depths through reset GP boundary')
 print('LIMIT: conditional address intersection only; live GP/SP, actual stack depth, memory accesses and reachability not established')
if __name__=='__main__':main()
