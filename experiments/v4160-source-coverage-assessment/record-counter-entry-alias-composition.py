#!/usr/bin/env python3
"""Conditional composition across an unchanged synthetic callback boundary."""
import argparse,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
entry=load('entry','record-counter-entry-107c6.py');machine=load('machine','record-counter-107d8-machine.py');m=machine.m
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();entry.validate(image);code={}
 for pc,h in m.WINDOWS:code.update({pc+i:b for i,b in enumerate(bytes.fromhex(h))})
 m.need(image[0x8814:0x8816]==bytes.fromhex('e9bf'),'return jump');code.update({0x10814:0xe9,0x10815:0xbf})
 count=0;clobbered=0
 for old in range(256):
  for threshold in range(256):
   for pos in range(4):
    # Incoming a0 points into the entry's own saved threshold word.
    sp=0x1000;counter=sp-20+pos;mem={counter:old}
    out=entry.enter(sp,0x11,0x22,0x33,counter,threshold,0x44,0x55,0x66,mem)
    actual=mem[counter];clobbered+=actual!=old
    pc,events=machine.execute(code,1,actual,threshold,sp=out['sp'],counter=counter,memory=mem)
    val,target=m.project(1,actual,threshold)
    m.need((pc,events[-1][2])==(target,val),'composition result')
    m.need(events[0]==('load8',counter,actual) and events[1]==('load32',sp-20,threshold),'read after entry writes')
    count+=1
 print(f'PASS: {count} entry/callback-return synthetic compositions; {clobbered} initial counter bytes overwritten before callback')
 print('LIMIT: callback assumed to return without changing frame/registers/memory; synthetic alias only, no reachability or hardware')
if __name__=='__main__':main()
