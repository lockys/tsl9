#!/usr/bin/env python3
"""Fixed instruction ledger for conditional V1.31 ReadCharCfg s0 preservation."""
import argparse,hashlib,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
s=importlib.util.spec_from_file_location('reference',HERE/'counter-reference-read-ccc.py');refmod=importlib.util.module_from_spec(s);s.loader.exec_module(refmod)
# Each entry is (PC, raw bytes, direct GPR destination or None).
# Xwchc interpretation is required at 0x4b460; this is a fixed ledger, not an ISA decoder.
LEDGER=((0x4b456,'4111',2),(0x4b458,'06c6',None),(0x4b45a,'eff0bfe8',1),(0x4b45e,'09c5',None),(0x4b460,'2821',10),(0x4b462,'b240',1),(0x4b464,'4101',2),(0x4b466,'8280',0),(0x4b468,'0145',10),(0x4b46a,'e5bf',0),(0x4b2e4,'b7370020',15),(0x4b2e8,'83c6573b',13),(0x4b2ec,'8147',15),(0x4b2ee,'63e5d700',None),(0x4b2f2,'0147',14),(0x4b2f4,'3a85',10),(0x4b2f6,'8280',0),(0x4b2f8,'2e87',14),(0x4b2fa,'9105',11),(0x4b2fc,'03d6c5ff',12),(0x4b300,'e30aa6fe',None),(0x4b304,'8507',15),(0x4b306,'e5b7',0))
def validate(image):
    for pc,h in refmod.WINDOWS:
        b=bytes.fromhex(h);refmod.need(image[pc-0x40000:pc-0x40000+len(b)]==b,'window')
    for start,end in ((0x4b456,0x4b46c),(0x4b2e4,0x4b308)):
        pos=start
        for pc,h,rd in (x for x in LEDGER if start<=x[0]<end):
            b=bytes.fromhex(h);refmod.need(pc==pos and image[pc-0x40000:pc-0x40000+len(b)]==b,'ledger coverage')
            refmod.need(rd!=8,'s0 destination');pos+=len(b)
        refmod.need(pos==end,'ledger end')
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);path=p.parse_args().root/refmod.REF
    if not path.exists():raise SystemExit('SKIP (nonzero): reference carrier unavailable')
    image=path.read_bytes();refmod.need(hashlib.sha256(image).hexdigest()==refmod.SHA,'reference identity');validate(image)
    for pc,h,_ in LEDGER:
        for offset in range(len(bytes.fromhex(h))):
            altered=bytearray(image);altered[pc-0x40000+offset]^=1
            try:validate(altered)
            except ValueError:continue
            raise ValueError('mutation accepted')
    print('PASS: 23 instruction ledger entries, 58 individual byte mutations rejected')
    print('LIMIT: fixed ledger under Xwchc, not a general decoder; s0 preservation requires correct control flow, valid stable stack, no traps or external effects; installed ROM and ISA unverified')
if __name__=='__main__':main()
