#!/usr/bin/env python3
"""Conditional V1.31 registration projection for b0fc's second call.

Hand projection based on existing static Xwchc interpretation, NOT a CPU
emulator. Requires candidate installed, previous calls return preserving live
state, successful accesses, no concurrency or problematic memory aliasing.
"""
import argparse,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
m=load('m','record-counter-107d8.py');slots=load('slots','callback-b0fc-reference-slots.py');model=load('model','callback-provider-b0fc-boundaries.py');dec=load('dec','callback-provider-b0fc-decoder.py')
BODY=bytes.fromhex('373700201307c7191c33342363ffd700b736002083a6461c1386170010b313972700369708c33e8582809307f00fe5bf')
def check_body(raw):m.need(raw[0x3c4e:0x3c7e]==BODY,'registration body')
def register(count,capacity,table,handler):
 if count>=capacity:return 255,count,None
 return count,count+1,((table+4*count)&MASK,handler)
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);root=p.parse_args().root;image=(root/m.BIN).read_bytes();m.validate(image);model.validate_local(image)
 name,path,digest,copy,fill=slots.ref.CANDIDATES[0];carrier=root/path
 if not carrier.exists():raise SystemExit('SKIP: V1.31 reference unavailable')
 raw=carrier.read_bytes();slots.verify(raw,digest,name,copy,fill);check_body(raw)
 for count in range(256):
  for cap in range(256):
   ret,new,write=register(count,cap,0x20002000,0xb0d0);mem,events=dec.execute(ret,0x200040c0,0x43c4e)
   m.need(mem[0x200040c0]==ret and new==(count+1 if count<cap else count),'state result')
   m.need(write==((0x20002000+4*count,0xb0d0) if count<cap else None),'registration write')
   m.need(events[2]==('load32',0x40080,0x43c4e),'candidate slot')
 for i in range(len(BODY)):
  data=bytearray(raw);data[0x3c4e+i]^=1
  try:check_body(data)
  except ValueError:continue
  raise ValueError('body mutation survived')
 print('PASS: 65536 count/capacity cases; 48 registration body byte mutations rejected')
 print('LIMIT: conditional Xwchc/static projection, not proof of installed resident, valid table, reachability, scheduling or callback execution')
if __name__=='__main__':main()
