#!/usr/bin/env python3
"""Conditional threshold-three counter invariant at the local return boundary."""
import argparse,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
s=importlib.util.spec_from_file_location('machine',HERE/'record-counter-107d8-machine.py');machine=importlib.util.module_from_spec(s);s.loader.exec_module(machine);m=machine.m

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();m.validate(image);code={}
 for pc,h in m.WINDOWS:code.update({pc+i:b for i,b in enumerate(bytes.fromhex(h))})
 m.need(image[0x8814:0x8816]==bytes.fromhex('e9bf'),'return jump');code.update({0x10814:0xe9,0x10815:0xbf})
 count=0
 for old in range(256):
  for ret in range(256):
   pc,events=machine.execute(code,ret,old,3);new=events[-1][2]
   m.need(new in (0,1,2),'invariant');m.need(pc in (0x107ee,0x107fc),'exit');count+=1
 # Prove closure and full transition matrix for both classes of callback result.
 observed={}
 for old in range(3):
  for ret in (0,1):
   pc,events=machine.execute(code,ret,old,3);observed[(old,ret)]=(pc,events[-1][2])
 expected={(0,0):(0x107ee,0),(1,0):(0x107ee,0),(2,0):(0x107ee,0),
           (0,1):(0x107ee,1),(1,1):(0x107ee,2),(2,1):(0x107fc,0)}
 m.need(observed==expected,'transition matrix')
 print(f'PASS: {count} counter/byte-return pairs enter 0..2; six exact closure transitions')
 print('LIMIT: threshold 3 at post-callback boundary, successful fixed-memory accesses; no concurrency, callback/provider side effects, state handling after 0x107fc, reachability or hardware proof')
if __name__=='__main__':main()
