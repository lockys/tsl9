#!/usr/bin/env python3
"""Finite TX byte-decoder traces with shared synthetic memory."""
import argparse,hashlib,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def load(name,file):
    s=importlib.util.spec_from_file_location(name,HERE/file);x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
machine=load('machine','tx-copy-machine.py');m=machine.m

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);root=p.parse_args().root
    raw=(root/m.BIN).read_bytes();m.need(len(raw)==76800 and hashlib.sha256(raw).hexdigest()==m.SHA,'identity');code={}
    for addr,h in m.WINDOWS:
        b=bytes.fromhex(h);m.need(raw[addr-0x8000:addr-0x8000+len(b)]==b,'instruction bytes');code.update({addr+i:v for i,v in enumerate(b)})
    for initial in range(256):
        r=[0]*32;r[8]=16;r[9]=0x1000;r[15]=0xffc;r[14]=7
        mem={0x1000+i:(initial+i)&255 for i in range(17)};oracle=mem.copy();idx=0;cs=7
        for i in range(16):
            pc,r,events=machine.execute(code,r,mem);expected=m.step(idx,16,0x1000,0xffc,cs,oracle);idx,cs=expected[1:3]
            m.need((pc,r[11],r[14],events)==expected and mem==oracle,'overlap trace')
            m.need(events[0][2]==initial,'forward propagation')
        pc,r,events=machine.execute(code,r,mem);m.need(pc==0x8b14 and not events,'exit')
    r=[0]*32;r[8]=65536;r[9]=0x100000;r[15]=0x200000
    mem={0x100000+i:i&255 for i in range(65537)}
    for i in range(65536):
        pc,r,events=machine.execute(code,r,mem)
        m.need(pc==0x8b0a and r[11]==i+1 and len(events)==2,'long trace')
    pc,r,events=machine.execute(code,r,mem)
    m.need(pc==0x8b0a and r[11]==65537 and events[0][1]==0x110000,'low16 rollover')
    print('PASS: 256 shared-memory overlap traces and 65537-step rollover trace')
    print('LIMIT: fixed instruction decoder, synthetic memory and successful sequential access; no actual infinite-loop, reachability, target exception or hardware proof')
if __name__=='__main__':main()
