#!/usr/bin/env python3
"""Conditional first exits of 0x155d0; instruction bytes are pinned, not emulated."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
WINDOWS = {
    0x155d0:'411126c2938441059c4006c622c483c747004ac0a18b81cb9307650093f7f70f0947636df71883c7611691cb2244b240924402492383011641016f2070301309f5ff1377f90f9d472a8463ebe70081465146814517050000130565f0',
    0x1578c:'b24022449244024941018280',
    0x18110:'05468d4501456ff09ff1',
    0x167d0:'03c51700efe0dfdf0904e31424ff',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def branch_target(raw, pc):
    w = int.from_bytes(raw,'little')
    need((w & 0x707f)==0x6063 and ((w>>15)&31)==14 and ((w>>20)&31)==15, 'not bltu a4,a5')
    imm = ((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    if imm & 0x1000:
        imm -= 0x2000
    return pc+imm


def check(image):
    for pc, text in WINDOWS.items():
        value=bytes.fromhex(text)
        need(image[pc-0x8000:pc-0x8000+len(value)] == value, f'window mismatch {pc:#x}')
    need(branch_target(image[0x155f2-0x8000:0x155f6-0x8000],0x155f2)==0x1578c,'first exit target')


def outcome(status, arg, flag, a1):
    # Entry argument is byte-sized only on the documented 0x167d0 route.
    if status & 8 and ((arg+6)&255)>2:
        return 'return-to-167d8',a1
    if flag:
        return 'tail-1802e',3
    return 'unanalysed',a1


def main():
    image=BIN.read_bytes()
    need(len(image)==76800 and hashlib.sha256(image).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','BIN identity')
    check(image)
    counts={'return-to-167d8':0,'tail-1802e':0,'unanalysed':0}
    for status in range(256):
        for arg in range(256):
            for flag in (0,1):
                a=outcome(status,arg,flag,1)
                b=outcome(status,arg,flag,0x2000c000)
                counts[a[0]]+=1
                need(a[0]==b[0], 'branch varies with a1')
                if a[0]=='tail-1802e':
                    need(a[1]==b[1]==3,'tail does not overwrite a1')
                else:
                    need(a[1]!=b[1], 'a1 difference lost')
    need(sum(counts.values())==131072 and all(counts.values()),'missing branch coverage')
    mutations=0
    for pc,text in WINDOWS.items():
        for i in range(len(bytes.fromhex(text))):
            changed=bytearray(image); changed[pc-0x8000+i]^=1
            try:
                check(changed)
            except ValueError:
                mutations+=1
            else:
                raise ValueError('mutated window accepted')
    print(f'PASS: 131072 synthetic (status, byte, flag) cases: {counts}')
    print(f'PASS: {mutations} local byte mutations rejected')
    print('LIMIT: conditional prefix projection, no CPU execution; unanalysed paths, later calls and tail-return callers remain unknown')


if __name__=='__main__':
    main()
