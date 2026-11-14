#!/usr/bin/env python3
"""Synthetic b0fc local-state stores aliasing tail's saved ra / slot.

No physical mapping, alignment, concurrency or reachability claim. Calls
are boundary stubs and all reads and writes are assumed successful.
"""
import argparse,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
m=load('m','record-counter-107d8.py');body=load('body','callback-provider-b0fc-decoder.py');tail=load('tail','callback-b0fc-tail-decoder.py')
def apply(mem,events):
 for e in events:
  if e[0]=='store8':mem[e[1]]=e[2]
  elif e[0]=='store16':
   for i in range(2):mem[(e[1]+i)&MASK]=(e[2]>>(8*i))&255

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();m.validate(image);body.model.validate_local(image)
 for value in range(256):
  sp=0x20001000;base=sp+12;mem={}
  for addr,v in ((sp+4,0x44444444),(sp+8,0x88888888),(sp+12,0x12345678),(0x4022c,0x1001)):tail.put(mem,addr,v)
  _,events=body.execute(value,base,0x43c4e);apply(mem,events);got=tail.execute(sp,0x40000,value,mem)
  m.need(got[4]==0x03030300|value and got[0]==0x1000,'saved ra alias')
  # A separate synthetic live gp places the four state bytes over the tail slot.
  base=0x4022c;mem={}
  for addr,v in ((sp+4,0x44444444),(sp+8,0x88888888),(sp+12,0x12345678),(0x4022c,0x87654321)):tail.put(mem,addr,v)
  _,events=body.execute(value,base,0x43c4e);apply(mem,events);got=tail.execute(sp,0x40000,value,mem)
  m.need(got[0]==((0x03030300|value)&~1) and got[4]==0x12345678,'tail slot alias')
 print('PASS: 256 saved-ra aliases and 256 tail-slot aliases, shared byte memory')
 print('LIMIT: synthetic address witnesses, unknown indirect calls stubbed; GP/SP reachability and real memory mapping unproven')
if __name__=='__main__':main()
