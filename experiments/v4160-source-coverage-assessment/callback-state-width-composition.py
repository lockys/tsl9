#!/usr/bin/env python3
"""Compose truncated state-byte writes with full-width state decisions."""
import argparse,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
store=load('store','callback-state-store-10766.py');branch=load('branch','callback-state-branch-1077e.py');m=store.model

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();store.validate(image);branch.validate_local(image)
 first_differences=0;second_differences=0
 for high in range(256):
  for low in range(256):
   full=high<<8|low
   a0,events,link,target=store.execute(store.CODE,full);a0low,lowevents,_,_=store.execute(store.CODE,low)
   m.need(a0==a0low and events==lowevents and (link,target)==(1,0x12b24),'low byte projection')
   first,second=branch.execute(full);lowfirst,lowsecond=branch.execute(low)
   first_differences+=first!=lowfirst;second_differences+=second!=lowsecond
   m.need(first==(0x10794 if full==0 else 0x10780) and second==(0x107a0 if full==6 else 0x107b8),'full width decisions')
 m.need((first_differences,second_differences)==(255,255),'difference count')
 print('PASS: 65536 full/low pairs; same stored bytes for each pair, 255 first-branch and 255 second-branch differences')
 print('LIMIT: separately decoded sites composed under returning providers and s0 preservation; no scheduling, reachability, interrupts or hardware proof')
if __name__=='__main__':main()
