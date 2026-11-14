#!/usr/bin/env python3
"""Conditional finite bound for TX copy with initial a1=0 and stable s0."""
import argparse,hashlib,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
s=importlib.util.spec_from_file_location('loop',HERE/'tx-copy-machine.py');machine=importlib.util.module_from_spec(s);s.loader.exec_module(machine);m=machine.m

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);root=p.parse_args().root
    raw=(root/m.BIN).read_bytes();m.need(len(raw)==76800 and hashlib.sha256(raw).hexdigest()==m.SHA,'identity');code={}
    for addr,h in m.WINDOWS:
        b=bytes.fromhex(h);m.need(raw[addr-0x8000:addr-0x8000+len(b)]==b,'instruction bytes');code.update({addr+i:v for i,v in enumerate(b)})
    # For n<=65535, 0<=i<n implies low16(i)=i<n, and low16(n)=n.
    for n in range(65536):
        m.need((n&65535)==n,'length representability')
        if n:m.need(((n-1)&65535)<n,'last copy')
        m.need(not ((n&65535)<n),'exit')
    for n in (0,1,2,255,256,1039,1040,65534,65535):
        r=[0]*32;r[8]=n;r[9]=0x100000;r[15]=0x200000
        mem={0x100000+i:i&255 for i in range(n)}
        for i in range(n):
            pc,r,events=machine.execute(code,r,mem);m.need(pc==0x8b0a and r[11]==i+1 and len(events)==2,'copy trace')
        pc,r,events=machine.execute(code,r,mem);m.need(pc==0x8b14 and r[11]==n and not events,'terminal gate')
    print('PASS: 65536 mathematical bounds; 9 decoder traces through terminal gate')
    print('LIMIT: conditional a1=0, stable s0<=65535, sequential successful noninterfering accesses; not reachability, provider preservation or hardware proof')
if __name__=='__main__':main()
