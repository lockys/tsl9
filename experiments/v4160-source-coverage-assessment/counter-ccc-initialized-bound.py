#!/usr/bin/env python3
"""Compose a reference candidate capacity store with the CCC counter witness."""
import argparse
import hashlib
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def load(filename):
    spec=importlib.util.spec_from_file_location('ccc_alias',Path(__file__).with_name(filename))
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
ccc=load('counter-reference-ccc-alias.py')
def need(ok,message):
    if not ok:raise ValueError(message)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=ROOT);root=parser.parse_args().root
    app=(root/ccc.APP).read_bytes();need(len(app)==76800 and hashlib.sha256(app).hexdigest()==ccc.APP_SHA,'APP identity')
    path=root/ccc.REF
    if not path.exists():raise SystemExit('SKIP (nonzero): reference carrier unavailable')
    reference=path.read_bytes();need(hashlib.sha256(reference).hexdigest()==ccc.REF_SHA,'reference identity')
    windows=ccc.WINDOWS+((0x4edd2,'b737002003c51720411122c437340020937735001304c43a09811cb4'),)
    for pc,h in windows:
        expected=bytes.fromhex(h);need(reference[pc-0x40000:pc-0x40000+len(expected)]==expected,'reference window')
    need(app[0x8faa-0x8000:0x8fb8-0x8000]==bytes.fromhex('832784134165938501087d158297'),'APP call')
    # Under the Xwchc interpretation, qk.c.sb stores low byte a5 at s0+9.
    need(0x20003000+0x3ac+9==0x200033b5,'capacity destination')
    for config in range(256):
        capacity=config&3
        need(0<=capacity<=3,'initializer capacity')
        need(ccc.project(capacity)[48]==1,'counter overwritten despite bounded capacity')
    need((0x0e&3)==2 and ccc.BASE+4*2==0x20004088,'nominal case')
    print('PASS: all 256 config bytes produce capacity 0..3; conditional 255-counter witness requires an intervening change or another initialization/provider')
    print('PASS: conditional nominal config 0x0e gives capacity 2, table end 0x20004088')
    print('LIMIT: candidate V1.31 and Xwchc only; capacity sampled after store assumed unchanged, valid accesses, no IRQ/DMA/alias or other writer; no live device proof')
if __name__=='__main__':main()
