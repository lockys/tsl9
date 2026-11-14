#!/usr/bin/env python3
"""Synthetic 0x1074c frame writes before 0xd272's indirect-slot read.

No claim that these SP values are valid, aligned, accessible or reachable.
The wrapper is stopped before its indirect target executes.
"""
import argparse,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff;SLOT=0x40048
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
m=load('m','record-counter-107d8.py');entry=load('entry','callback-state-entry-1074c.py');wrapper=load('wrapper','callback-provider-d272-decoder.py')
def word(mem,addr):return sum(mem.get((addr+i)&MASK,0)<<(8*i) for i in range(4))
def run(sp,old_ra,old_s0,input_value,slot):
 mem={(SLOT+i)&MASK:(slot>>(8*i))&255 for i in range(4)}
 new_sp,s0=entry.enter(sp,old_ra,old_s0,input_value,mem)
 loaded=word(mem,SLOT)
 result=wrapper.execute(wrapper.CODE,loaded,0x10758)
 return new_sp,s0,loaded,result

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();m.validate(image);entry.validate_local(image);wrapper.validate_local(image);m.need(entry.calls()[0]==(1,0xd272),'first call target')
 cases=0
 for sp in range(SLOT-12,SLOT+17):
  for k in range(256):
   old_ra=(0x11223300|k);old_s0=(0xaabbcc00|k);slot=0x98765433
   newsp,s0,loaded,result=run(sp,old_ra,old_s0,k,slot)
   expected=list(slot.to_bytes(4,'little'))
   for addr,value in (((sp-4)&MASK,old_ra),((sp-8)&MASK,old_s0)):
    for i,b in enumerate(value.to_bytes(4,'little')):
     dest=(addr+i)&MASK
     if SLOT<=dest<SLOT+4:expected[dest-SLOT]=b
   m.need(newsp==(sp-16)&MASK and s0==k and loaded==int.from_bytes(expected,'little'),'frame alias')
   m.need(result[:5]==(0x2000bf48,0,19,loaded&~1,0x10758),'slot read or wrapper arguments');cases+=1
 m.need(run(SLOT+4,0x12345679,0xaabbccdd,0,0x98765433)[2]==0x12345679,'saved ra alias')
 m.need(run(SLOT+8,0x12345679,0xaabbccdd,0,0x98765433)[2]==0xaabbccdd,'saved s0 alias')
 print('PASS:',cases,'synthetic SP/value cases; saved ra and saved s0 slot-alias witnesses')
 print('LIMIT: models memory as ordinary bytes with successful writes/read; alignment, traps, MMIO, reachable SP and indirect execution unproven')
if __name__=='__main__':main()
