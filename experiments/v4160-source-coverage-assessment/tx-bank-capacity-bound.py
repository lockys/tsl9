#!/usr/bin/env python3
"""Conditional numeric TX bank bounds, not a memory ownership claim."""
import argparse,hashlib,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
s=importlib.util.spec_from_file_location('entry',HERE/'tx-entry-length-guard.py');entry=importlib.util.module_from_spec(s);s.loader.exec_module(entry)
s=importlib.util.spec_from_file_location('store',HERE/'tx-checksum-store.py');store=importlib.util.module_from_spec(s);s.loader.exec_module(store)
BASE=0x2000b18c;STRIDE=1062

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);root=p.parse_args().root
    image=(root/entry.BIN).read_bytes();entry.need(len(image)==76800 and hashlib.sha256(image).hexdigest()==entry.SHA,'image identity');entry.decode(image[0xa56:0xa74])
    # Fixed original header/checksum windows establish these arithmetic offsets.
    raw=bytes.fromhex('93076042b307f602972600209386666b6177134757f59375f40f9907b6972390e7002382b70013578400ce95a381e7002e97238137011377f70f8145')
    entry.need(image[0xace:0xb0a]==raw,'header window');store.decode(image[0xb14:0xb1a])
    for bank in range(2):
        b=BASE+bank*STRIDE;start=b+11
        for n in range(1040):
            end=start+n;metadata=set(range(b+2,b+6));payload=set(range(start,end));checksum={end}
            entry.need(store.project(b+6,n,0)[0]==end,'checksum instruction address')
            entry.need(end<b+STRIDE and not (metadata & (payload|checksum)),'bank bounds')
            entry.need(all(b<=x<b+STRIDE for x in payload|checksum),'contained')
        print('bank',bank,'start',hex(start),'max checksum',hex(start+1039),'remaining bytes',STRIDE-(11+1039+1))
    print('PASS: 2080 bank/length cases; payload and checksum separated from metadata')
    print('LIMIT: assumes bank 0/1, post-provider length equals accepted length, normal loop completion and header address equations; no source non-alias, ownership or hardware proof')
if __name__=='__main__':main()
