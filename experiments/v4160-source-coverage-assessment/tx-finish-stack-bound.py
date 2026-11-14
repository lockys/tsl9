#!/usr/bin/env python3
"""Conditional address arithmetic for descriptor/saved-s0 overlap."""
import argparse,hashlib,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];M=0xffffffff
def load(name,path):
    s=importlib.util.spec_from_file_location(name,HERE/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
meta=load('meta','tx-finish-metadata.py');tail=load('tail','tx-finish-tail.py');entry=tail.entry
BASE=0x2000b18c;STRIDE=1062
def byte_set(addr,n):return {(addr+i)&M for i in range(n)}
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);img=(p.parse_args().root/entry.BIN).read_bytes()
    entry.need(len(img)==76800 and hashlib.sha256(img).hexdigest()==entry.SHA,'identity');meta.window(img[0xb1a:0xb3a]);tail.verify(img[0xb3a:0xb52])
    slot=byte_set(0x40050,4)
    for bank in range(2):
        events=meta.events(bank,BASE,0);writes=set().union(*(byte_set(a,w) for a,w,v in events))
        entry.need(writes==byte_set(BASE+bank*STRIDE+2,4) and not writes&slot,'descriptor bounds')
        # Integer modular inverse: some of the four saved bytes must equal one written byte.
        overlaps={((w-24-k)&M) for w in writes for k in range(4)}
        entry.need(len(overlaps)==7,'set size')
        for sp in [*((BASE+bank*STRIDE-40+i)&M for i in range(80)),0,0xfffffffc,0xffffffff]:
            observed=bool(byte_set((sp+24)&M,4)&writes)
            entry.need(observed==(sp in overlaps),'overlap')
        print('bank',bank,'descriptor',hex(min(writes))+'..'+hex(max(writes)),'overlapping sp',hex(min(overlaps))+'..'+hex(max(overlaps)))
    print('PASS: two conditional bank addresses, exact seven-SP overlap sets, boundary and wrap checks')
    print('LIMIT: assumes live a2=bank and a3=0x2000b18c at descriptor writes; no provider preservation, stack alignment, physical memory or reachability proof')
if __name__=='__main__':main()
