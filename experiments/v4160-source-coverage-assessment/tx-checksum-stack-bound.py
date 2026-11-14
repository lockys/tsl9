#!/usr/bin/env python3
"""Conditional checksum-to-saved-stack overlap address envelope."""
import argparse,hashlib,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];M=0xffffffff
def load(name,path):
 s=importlib.util.spec_from_file_location(name,HERE/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
store=load('store','tx-checksum-store.py');entry=load('entry','tx-entry-length-guard.py')
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);img=(p.parse_args().root/entry.BIN).read_bytes()
 entry.need(len(img)==76800 and hashlib.sha256(img).hexdigest()==entry.SHA,'identity');entry.decode(img[0xa56:0xa74]);store.decode(img[0xb14:0xb1a])
 for bank in range(2):
  base=0x2000b18c+bank*1062;possible=set()
  for n in range(1040):
   address,_,_=store.project(base+6,n,0)
   # Restored stack words: s3 +12, s2 +16, s1 +20, s0 +24, ra +28.
   for offset in (12,16,20,24,28):
    for byte in range(4):possible.add((address-offset-byte)&M)
  # Adjacent restored words yield one contiguous byte range.
  lo=base+11-31;hi=base+11+1039-12
  entry.need(possible==set(range(lo,hi+1)),'stack envelope')
  aligned=[sp for sp in possible if sp%4==0 and sp<=0x20010000]
  distance=0x20010000-max(aligned)
  print('bank',bank,'SP',hex(lo),'..',hex(hi),'nearest aligned depth from 0x20010000',distance,'bytes')
 print('PASS: 2080 checksum addresses and exact modular inverse stack envelope')
 print('LIMIT: assumes bank 0/1, live a5=bank base+6 and s0=0..1039; depth is arithmetic from 0x20010000, not a measured stack bound; no proof of actual SP, memory validity, alignment traps or reachability')
if __name__=='__main__':main()
