#!/usr/bin/env python3
"""Conditional f7 zero-object tail to resident slot 0x40070."""
import hashlib
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import case_f7_provider as previous

PC=0x943e
CODE=bytes.fromhex('19453305a402b70704002244b24003a3070741010283')


def need(ok,message):
    if not ok:
        raise ValueError(message)


def validate(data):
    previous.validate(data)
    need(data[PC-0x8000:PC-0x8000+len(CODE)]==CODE,'tail bytes mismatch')


def project(pointer,a1,slot):
    if pointer!=0:
        return ('outside-zero-path',a1)
    return ('tail-40070',12,a1,slot&0xfffffffe)


def main():
    data=previous.BIN.read_bytes()
    need(len(data)==76800 and hashlib.sha256(data).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','BIN identity')
    validate(data)
    for a1 in range(65536):
        for pointer in (0,1,0xffffffff):
            result=project(pointer,a1,0x12345679)
            if pointer:
                need(result==('outside-zero-path',a1),'wrong selection')
            else:
                need(result==('tail-40070',12,a1,0x12345678),'wrong args')
    for i in range(len(CODE)):
        altered=bytearray(data);altered[PC-0x8000+i]^=1
        try: validate(altered)
        except ValueError: continue
        raise ValueError('mutation accepted')
    print(f'PASS: 196608 synthetic pointer/a1 projections; {len(CODE)} tail-byte mutations rejected')
    print('LIMIT: f7 case/zero word, stable nonaliasing data and successful accesses assumed; no provider execution or hardware')


if __name__=='__main__':
    main()
