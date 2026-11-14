#!/usr/bin/env python3
"""Conditional callback-checksum and post-return counter composition."""
import argparse,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
callback=load('callback','record-counter-callback-checksum.py');machine=load('machine','record-counter-107d8-machine.py');m=machine.m

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();callback.validate(image);m.validate(image);code={}
 for pc,h in m.WINDOWS:code.update({pc+i:b for i,b in enumerate(bytes.fromhex(h))})
 m.need(image[0x8814:0x8816]==bytes.fromhex('e9bf'),'return jump');code.update({0x10814:0xe9,0x10815:0xbf})
 count=0;accepted=0
 for old in range(256):
  for candidate in range(256):
   src=bytearray(11);src[2]=8;src[3]=0xa7;src[10]=candidate
   ret=callback.predicate(src);pc,events=machine.execute(code,ret,old,3)
   expected=(old+1)&255
   if not ret:expected=0;target=0x107ee
   elif expected>=3:expected=0;target=0x107fc
   else:target=0x107ee
   m.need((pc,events[-1][2])==(target,expected),'composition');accepted+=ret;count+=1
 print(f'PASS: {count} synthetic callback/counter compositions; {accepted} checksum matches')
 print('LIMIT: hand-written callback projection and limited counter decoder, normal callback return with stable registers/frame and non-alias memory; no reachability or hardware proof')
if __name__=='__main__':main()
