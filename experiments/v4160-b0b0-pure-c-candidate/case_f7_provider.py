#!/usr/bin/env python3
"""Conditional fixed-byte projection from dispatch entry f7 to resident call boundary."""
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BIN=ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
WINDOWS={
    0x1563c:'175700001307870b0a093a9983270900ba978287',
    0x162fe:'0545ef304f95',
    0x9454:'411122c406c626c2cd472a8463efa7049374f50f138514001375f50f4537',
    0x9410:'4111973700209387a7aa22c42a84884b06c611cdb7070400bc578297',
    0x1aacc:'0abcffff',
}


def require(condition,message):
    if not condition:
        raise ValueError(message)


def jal_target(data,pc):
    w=int.from_bytes(data,'little')
    require(w&0xfff==0xef,'not jal ra')
    imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    return pc+imm-(0x200000 if imm&0x100000 else 0)


def validate(data):
    for pc,hexbytes in WINDOWS.items():
        expected=bytes.fromhex(hexbytes)
        require(data[pc-0x8000:pc-0x8000+len(expected)]==expected,f'changed bytes at {pc:#x}')
    table=0x1a6f4
    require(table+4*0xf6==0x1aacc,'table entry address')
    relative=int.from_bytes(data[0x1aacc-0x8000:0x1aad0-0x8000],'little',signed=True)
    require((table+relative)&0xffffffff==0x162fe,'entry target')
    require(jal_target(data[0x16300-0x8000:0x16304-0x8000],0x16300)==0x9454,'call target')
    # The compressed 0x3745 at 0x9470 is pinned above; it is c.jal 0x9410.
    require((0x9412+0x20003000-1366+16)&0xffffffff==0x2000becc,'object word address')


def project(pointer,a1,slot):
    if pointer==0:
        return ('zero-branch',None,None)
    return ('jalr-40068',pointer,slot&0xfffffffe,a1)


def main():
    data=BIN.read_bytes()
    require(len(data)==76800 and hashlib.sha256(data).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','BIN identity')
    validate(data)
    for low in range(65536):
        a1=0x12340000|low
        for pointer in (0,1,0x20001234,0xffffffff):
            result=project(pointer,a1,0x12345679)
            require(result[0]==('zero-branch' if pointer==0 else 'jalr-40068'),'branch')
            if pointer:
                require(result[1:]==(pointer,0x12345678,a1),'call projection')
    n=0
    for pc,hexbytes in WINDOWS.items():
        for i in range(len(bytes.fromhex(hexbytes))):
            changed=bytearray(data);changed[pc-0x8000+i]^=1
            try: validate(changed)
            except ValueError: n+=1
            else: raise ValueError('mutation accepted')
    print(f'PASS: 262144 synthetic pointer/a1 projections; {n} local byte mutations rejected')
    print('LIMIT: f7 dispatch and ordinary memory/no alias/no interruption assumed; no callee or provider execution')


if __name__=='__main__':
    main()
