#!/usr/bin/env python3
"""Conditional composition of entry guard, reference ledger and copy gate."""
import argparse,hashlib,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def load(name,file):
    spec=importlib.util.spec_from_file_location(name,HERE/file);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
entry=load('entry','tx-entry-length-guard.py');ledger=load('ledger','tx-reference-ccc-s0.py');mach=load('mach','tx-copy-machine.py');m=mach.m

def copy_code(image):
    code={}
    for pc,h in m.WINDOWS:
        b=bytes.fromhex(h);entry.need(image[pc-0x8000:pc-0x8000+len(b)]==b,'copy window');code.update({pc+i:v for i,v in enumerate(b)})
    return code

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);root=p.parse_args().root
    image=(root/entry.BIN).read_bytes();entry.need(len(image)==76800 and hashlib.sha256(image).hexdigest()==entry.SHA,'app identity');entry.decode(image[0xa56:0xa74])
    path=root/ledger.refmod.REF
    if not path.exists():raise SystemExit('SKIP (nonzero): reference carrier unavailable')
    ref=path.read_bytes();entry.need(hashlib.sha256(ref).hexdigest()==ledger.refmod.SHA,'reference identity');ledger.validate(ref)
    code=copy_code(image)
    for length in range(1040):
        # Explicit assumption: actual calls return preserving s0, and nothing
        # between the projections modifies it. Test terminal and last gate.
        for idx in ({0} if not length else {length-1,length}):
            r=[0]*32;r[8]=length;r[9]=0x100000;r[11]=idx;r[15]=0x200000
            pc,out,events=mach.execute(code,r,{0x100000+idx:0x5a})
            entry.need(pc==(0x8b0a if idx<length else 0x8b14),'branch')
            entry.need(len(events)==(2 if idx<length else 0),'accesses')
    print('PASS: all 1040 accepted entry lengths; copy last/terminal gates checked against decoded instructions')
    print('LIMIT: conditional reference Xwchc ledger, normal returns preserving s0, stable state and successful access; segmented projection, not installed ROM, reachability or hardware')
if __name__=='__main__':main()
