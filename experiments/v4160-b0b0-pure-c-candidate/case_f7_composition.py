#!/usr/bin/env python3
"""Conditionally compose existing fixed-byte projections, stopping at provider boundary."""
import hashlib
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import callee_155d0_prefix as prefix
import callee_155d0_dispatch as dispatch
import case_f7_provider as provider


def need(ok,message):
    if not ok:
        raise ValueError(message)


def run(status,flag,pointer,a1):
    gate,value=prefix.outcome(status,0xf7,flag,a1)
    if gate!='unanalysed':
        return gate,value
    selected,value=dispatch.dispatch(0xf7,value)
    need(selected=='table-read-15648','wrong table branch')
    result=provider.project(pointer,value,0x12345679)
    if result[0]=='zero-branch':
        return 'pointer-zero',value
    return 'provider',result[3]


def main():
    image=prefix.BIN.read_bytes()
    need(len(image)==76800 and hashlib.sha256(image).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','BIN identity')
    prefix.check(image);dispatch.check(image);provider.validate(image)
    counts={'return-to-167d8':0,'tail-1802e':0,'pointer-zero':0,'provider':0}
    for status in range(256):
        for flag in range(256):
            for pointer in (0,1,0x20001234,0xffffffff):
                old=run(status,flag,pointer,0x12345678)
                candidate=run(status,flag,pointer,0x2000c000)
                expected=('return-to-167d8' if status&8 else 'tail-1802e' if flag else 'pointer-zero' if not pointer else 'provider')
                need(old[0]==candidate[0]==expected,'selection mismatch')
                if expected=='tail-1802e':
                    need(old[1]==candidate[1]==3,'tail a1')
                else:
                    need(old[1]==0x12345678 and candidate[1]==0x2000c000,'a1 provenance')
                counts[expected]+=1
    need(counts=={'return-to-167d8':131072,'tail-1802e':130560,'pointer-zero':128,'provider':384},'unexpected counts')
    print(f'PASS: 262144 synthetic f7 compositions: {counts}')
    print('PASS: provider boundary iff !(status & 8), flag == 0, pointer != 0')
    print('LIMIT: independently projected segments, fixed input/state, successful ordinary nonaliasing accesses; no continuous CPU, provider or hardware')


if __name__=='__main__':
    main()
