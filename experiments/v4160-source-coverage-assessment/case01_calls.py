"""Case 0/1 call sequence, with both external callees stubbed at return.

Fixed original instruction fragments and local call targets are checked. This
is not continuous CPU execution and makes no callee side-effect claims.
"""
import hashlib
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('case',HERE/'table_case_entry.py')
case=importlib.util.module_from_spec(spec); spec.loader.exec_module(case)


def cj(pc,code):
    if len(code)!=2: raise ValueError('bad jump length')
    h=int.from_bytes(code,'little')
    if h&3!=1 or h>>13!=5: raise ValueError('not C.J')
    imm=((h>>12&1)<<11)|((h>>11&1)<<4)|((h>>9&3)<<8)|((h>>8&1)<<10)|((h>>7&1)<<6)|((h>>6&1)<<7)|((h>>3&7)<<1)|((h>>2&1)<<5)
    return pc+(imm-4096 if imm&2048 else imm)


def jal(pc,code):
    if len(code)!=4: raise ValueError('bad call length')
    w=int.from_bytes(code,'little')
    if w&0xfff!=0xef: raise ValueError('not JAL ra')
    imm=((w>>31&1)<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1)
    return pc+(imm-(1<<21) if imm&(1<<20) else imm)


def run(image,index,handle):
    if index not in (0,1): raise ValueError('unsupported case')
    def get(pc,n): return image[pc-0x8000:pc-0x8000+n]
    pc=(0x1452e,0x1453e)[index]
    first=case.entry(pc,get(pc,8),handle)
    if index==0:
        if get(0x14536,2)!=bytes.fromhex('0145'): raise ValueError('case 0 a0 setup')
        value=0
    else:
        if get(0x14546,2)!=bytes.fromhex('0945'): raise ValueError('case 1 a0 setup')
        value=2
        if get(0x14548,2)!=bytes.fromhex('c5bf') or cj(0x14548,get(0x14548,2))!=0x14538: raise ValueError('case 1 shared tail')
    if get(0x14538,4)!=bytes.fromhex('efe08fd9'): raise ValueError('second call mismatch')
    second=(jal(0x14538,get(0x14538,4)),value,0x1453c)
    if get(0x1453c,2)!=bytes.fromhex('b1be'): raise ValueError('exit jump mismatch')
    return first,second,cj(0x1453c,get(0x1453c,2))


def main():
    image=case.dispatch.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=case.dispatch.SHA: raise ValueError('APP identity mismatch')
    for index in (0,1):
        pc=(0x1452e,0x1453e)[index]
        for handle in range(65536):
            expected=((0x13ba6,handle,(0,3)[index],pc+8),(0x12ad0,(0,2)[index],0x1453c),0x14098)
            if run(image,index,handle)!=expected: raise ValueError('call projection mismatch')
        for handle in (0x10000,0xffffffff):
            if run(image,index,handle)[0][1]!=handle: raise ValueError('handle width mismatch')
    for lo,hi in ((0x1452e,0x1453e),(0x1453e,0x1454a)):
        for pc in range(lo,hi):
            bad=bytearray(image); bad[pc-0x8000]^=1
            try: run(bad,0 if lo==0x1452e else 1,5)
            except ValueError: continue
            raise ValueError(f'instruction mutation accepted at {pc:#x}')
    print('PASS: 131072 case/handle combinations, 4 full-width boundaries, 28 instruction byte mutations')
    print('Cases 0/1 call 0x13ba6 then 0x12ad0 with a0=0/2, then branch to 0x14098, if callees return.')
    print('Callees are stubbed; no reachability, ABI or hardware claim.')

if __name__=='__main__': main()
