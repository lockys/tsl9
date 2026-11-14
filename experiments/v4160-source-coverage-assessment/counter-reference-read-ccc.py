#!/usr/bin/env python3
"""Conditional WCH V1.31 ReadCharCfg reference semantics, not device ROM."""
import argparse,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REF='analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin'
SHA='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'
WINDOWS=((0x4013c,'56b40400'),(0x4b456,'411106c6eff0bfe809c52821b240410182800145e5bf'),(0x4b2e4,'b737002083c6573b814763e5d70001473a8582802e87910503d6c5ffe30aa6fe8507e5b7'))
def need(v,msg):
    if not v:raise ValueError(msg)
def project(handle,records,capacity,base=0x20004080):
    reads=[]
    for i in range(capacity):
        ptr=(base+4*i)&0xffffffff;h,value=records[i];reads.append(('halfword',ptr))
        if h==handle:
            if ptr==0:return 0,reads
            reads.append(('byte',(ptr+2)&0xffffffff));return value,reads
    return 0,reads
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);path=p.parse_args().root/REF
    if not path.exists():raise SystemExit('SKIP (nonzero): reference carrier unavailable')
    ref=path.read_bytes();need(hashlib.sha256(ref).hexdigest()==SHA,'reference identity')
    for pc,h in WINDOWS:
        b=bytes.fromhex(h);need(ref[pc-0x40000:pc-0x40000+len(b)]==b,'reference window')
    for capacity in range(256):
        records=[(i, (i*17)&255) for i in range(255)]
        for h in (0,capacity//2,254,255,0x10000):
            val,events=project(h,records,capacity)
            found=h<capacity
            need(val==((h*17)&255 if found else 0),'return')
            need(len(events)==(h+2 if found else capacity),'read count')
    records=[(9,7),(9,1)];need(project(9,records,2)[0]==7,'first duplicate')
    need(project(9,records,2,0)==(0,[('halfword',0)]),'null match')
    print('PASS: 1280 capacity/handle cases, first-match and null-pointer controls')
    print('LIMIT: reference candidate only, Xwchc interpretation assumed, successful aligned accesses and stable records/capacity; not installed ROM, hardware execution or reachability')
if __name__=='__main__':main()
