#!/usr/bin/env python3
"""Conditional composition across a provider boundary with then-live state."""
import argparse,hashlib,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def load(name,filename):
    s=importlib.util.spec_from_file_location(name,HERE/filename);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
call=load('call8a82','counter-precheck-provider-8a82.py')
nextpart=load('next8a96','counter-precheck-provider-next-8a96.py')
def need(v,msg):
    if not v:raise ValueError(msg)
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/call.BIN).read_bytes()
    need(len(image)==76800 and hashlib.sha256(image).hexdigest()==call.SHA,'APP identity')
    need(call.decode(image[0xa82:0xa96])==0x4013c,'call slot');nextpart.decode(image[0xa96:0xa9e])
    for h in range(65536):
        initial_gp=0x20004000;initial_s2=h
        # Hypothetical provider returns 0 after changing the live comparison
        # register and gp; we do not claim this respects an ABI or occurs.
        result=call.boundary(initial_gp,h,0x40001,0)
        need(result[-1]==0x8a96,'fallthrough')
        addr,_,pc=nextpart.project(initial_gp+4,(h+1)&0xffffffff,h)
        need(addr==0x2000409e and pc==0x8abe,'changed state')
        stale=nextpart.project(initial_gp,initial_s2,h)
        need(stale[0]==0x2000409a and stale[2]==0x8a9e,'stale-state control')
    print('PASS: 65536 synthetic provider-boundary cases distinguish then-live from stale GP/s2')
    print('LIMIT: hypothetical provider changes are not demonstrated; segmented projections are not continuous CPU execution, provider ABI, reachability or hardware proof')
if __name__=='__main__':main()
