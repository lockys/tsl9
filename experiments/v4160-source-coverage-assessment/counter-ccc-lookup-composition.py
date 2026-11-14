#!/usr/bin/env python3
"""Conditional composition of candidate CCC clearing and original APP lookup."""
import argparse
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def load(name,filename):
    spec=importlib.util.spec_from_file_location(name,Path(__file__).with_name(filename))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
ccc=load('counter_ccc','counter-reference-ccc-alias.py')
lookup=load('counter_lookup','counter-index-envelope.py')
def need(ok,msg):
    if not ok:raise ValueError(msg)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=ROOT);root=parser.parse_args().root
    app=(root/lookup.BIN).read_bytes();groups=lookup.classify(app)
    refpath=root/ccc.REF
    if not refpath.exists():raise SystemExit('SKIP (nonzero): reference carrier unavailable')
    import hashlib
    reference=refpath.read_bytes();need(hashlib.sha256(reference).hexdigest()==ccc.REF_SHA,'reference identity')
    for pc,hexbytes in ccc.WINDOWS:
        expected=bytes.fromhex(hexbytes);need(reference[pc-0x40000:pc-0x40000+len(expected)]==expected,'reference bytes')
    need(app[0x8faa-0x8000:0x8fb8-0x8000]==bytes.fromhex('832784134165938501087d158297'),'APP call site')
    indexed={index:(group,addr) for group,entries in groups.items() for index,addr in entries}
    for cap in range(256):
        idx=ccc.project(cap)[48];group,addr=indexed[idx]
        want=('outside_image',0x1ad46) if cap>=13 else ('known',0x1ab4a)
        need((group,addr)==want,'composition mismatch')
    print('PASS: 256 synthetic capacities; 13..255 yield counter 255 and lookup address 0x1ad46, 0..12 preserve counter 1 and address 0x1ab4a')
    print('LIMIT: reconstructed boundary only; assumes candidate installed, Xwchc, GP, live capacity, completed accesses, later lookup and no intervening writes; no physical fault or device conclusion')
if __name__=='__main__':main()
