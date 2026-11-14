#!/usr/bin/env python3
"""Pin and inspect two reference 0x40068 candidates; these are not a device dump."""
import argparse
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CASES=(
 ('analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22',0x431ba,'411122c426c23744024006c68324c420232604200f10000009e9232694201545b24022449244410182800347e5ff9307f00f6306f700232694201145d5b797d0fb1fe78080f1014523269420d1bf'),
 ('analysis/wch-resident-candidate-2026-10-21/carrier/REFERENCE-CANDIDATE-ONLY-00040000-0006EC56.bin','b02cf8ec6829425a558887bd6bc10d28ae1f0e2e9e1850333f0bab6088e9e941',0x43246,'411122c426c23744024006c68324c420232604200f10000009e9232694201545b24022449244410182800347e5ff9307f00f6306f700232694201145d5b797d0fb1fe780c0e8014523269420d1bf'),
)


def need(ok,message):
    if not ok: raise ValueError(message)


def far_target(pair,pc):
    upper=int.from_bytes(pair[:4],'little'); lower=int.from_bytes(pair[4:],'little')
    need(upper&0xfff==0x97,'not auipc ra')
    need(lower&0xfffff==0x80e7,'not jalr ra,ra')
    hi=upper&0xfffff000
    lo=(lower>>20)&0xfff
    if lo&0x800: lo-=0x1000
    return (pc+hi+lo)&0xfffffffe


def check(data,digest,address,expected):
    need(hashlib.sha256(data).hexdigest()==digest,'carrier hash mismatch')
    need(int.from_bytes(data[0x68:0x6c],'little')==address,'slot mismatch')
    off=address-0x40000
    body=data[off:off+len(expected)]
    need(body==expected,'body mismatch')
    call=body.index(bytes.fromhex('97d0fb1f'))
    need(far_target(body[call:call+8],address+call)==0x20000110,'helper target mismatch')
    return call


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=ROOT,help='repository containing reference carriers')
    root=parser.parse_args().root
    tested=0
    for path,digest,address,text in CASES:
        file=root/path
        if not file.is_file():
            raise SystemExit(f'SKIP: missing reference carrier {path}')
        data=file.read_bytes(); expected=bytes.fromhex(text)
        call=check(data,digest,address,expected)
        for offset in [0x68,0x69,0x6a,0x6b,*range(address-0x40000,address-0x40000+len(expected))]:
            changed=bytearray(data);changed[offset]^=1
            try: check(changed,digest,address,expected)
            except ValueError: continue
            raise ValueError('mutated carrier accepted')
        print(f'PASS: reference slot 0x40068 -> {address:#x}; {len(expected)} body bytes, helper at {address+call:#x} -> 0x20000110; {len(expected)+4} mutations rejected by carrier hash')
        tested+=1
    need(tested==2,'incomplete candidate set')
    print('LIMIT: fixed reference bytes only, no device ROM or helper execution, no complete a1-use proof')


if __name__=='__main__': main()
