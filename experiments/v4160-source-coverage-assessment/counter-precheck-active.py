#!/usr/bin/env python3
"""Conditional active-path return of queue precheck, with provider calls stubbed."""
import argparse,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
def need(v,msg):
    if not v:raise ValueError(msg)
def project(entries,length):
    value=0;calls=[]
    for i,(handle,kind,active) in enumerate(entries):
        if handle==0xfffe or kind!=2 or active==0:continue
        value=active
        if length<=8:calls.append(i)
    return value,tuple(calls)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=ROOT);image=(ap.parse_args().root/BIN).read_bytes()
    need(len(image)==76800 and hashlib.sha256(image).hexdigest()==SHA,'APP identity')
    # Pin qualification, flag capture before the unsigned length branch, the
    # call sites and the two-iteration return; these bytes are not executed.
    windows=((0x8308,'13142900569483572400638cf904834754006318fb048347440093f7f70fb1c303c624003e8a63eecb02'),(0x834e,'83a7cc0413056100829783c6240003552400500089069305000cfd25'),(0x836a,'63000902f25062545285'),(0x838a,'0549b5bf'))
    for pc,h in windows:
        raw=bytes.fromhex(h);need(image[pc-0x8000:pc-0x8000+len(raw)]==raw,f'instruction mismatch {pc:x}')
    count=0
    for length in range(256):
        for first in range(256):
            for second in (0,1,255):
                records=((0,2,first),(1,2,second));actual=project(records,length)
                last=second if second else first
                expected_calls=tuple(i for i,v in enumerate((first,second)) if v and length<=8)
                need(actual==(last,expected_calls),'conditional return or call count');count+=1
    # The later qualifying entry takes precedence; an invalid handle or wrong
    # type must not overwrite the previous active value.
    need(project(((0,2,7),(0xfffe,2,9)),8)==(7,(0,)),'sentinel')
    need(project(((0,2,7),(1,1,9)),9)==(7,()),'type/length')
    print(f'PASS: {count} synthetic length/active combinations, plus sentinel/type boundaries')
    print('LIMIT: qualifying calls modeled as normal-returning stubs preserving state and memory; no provider, MMIO, exceptions or hardware execution')
if __name__=='__main__':main()
