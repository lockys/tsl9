#!/usr/bin/env python3
"""Shared-memory witness: counter may overlap saved threshold bytes.
Synthetic addresses only; no claim of alignment, reachability or hardware behavior.
"""
import argparse,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
s=importlib.util.spec_from_file_location('machine',HERE/'record-counter-107d8-machine.py');machine=importlib.util.module_from_spec(s);s.loader.exec_module(machine);m=machine.m

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();m.validate(image);code={}
 for addr,h in m.WINDOWS:
  data=bytes.fromhex(h);code.update({addr+i:b for i,b in enumerate(data)})
 m.need(image[0x8814:0x8816]==bytes.fromhex('e9bf'),'return jump');code.update({0x10814:0xe9,0x10815:0xbf})
 cases=0;changed=0
 for sp in (0x1000,0xfffffff0,0xfffffff4,0xfffffffc):
  for index in range(4):
   addr=(sp+12+index)&machine.MASK
   for old in range(256):
    for ret in (0,1,0xffffffff):
     mem={(sp+12+i)&machine.MASK:0 for i in range(4)};mem[addr]=old
     before=sum(mem[(sp+12+i)&machine.MASK]<<(8*i) for i in range(4))
     pc,events=machine.execute(code,ret,old,0,sp=sp,counter=addr,memory=mem)
     new,target=m.project(ret,old,before)
     m.need((pc,events[-1])==(target,('store8',addr,new)),'result');m.need(mem[addr]==new,'store')
     if ret:
      m.need(events[:2]==[('load8',addr,old),('load32',(sp+12)&machine.MASK,before)],'read order')
      after=sum(mem[(sp+12+i)&machine.MASK]<<(8*i) for i in range(4));changed+=before!=after
     else:m.need(len(events)==1,'zero path must not load')
     cases+=1
 print(f'PASS: {cases} shared-memory cases; {changed} nonzero-return cases change saved threshold after it was read')
 print('LIMIT: synthetic alias and modular addresses; no claim of real reachability, aligned access, callback effects or hardware')
if __name__=='__main__':main()
