"""Conditional 0x12ad0 continuations after first call returns.

Fixed byte projections, not a general CPU emulator. SP and saved RA are
assumed preserved by the external callee; no callee effects are modelled.
"""
import hashlib
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('entry',HERE/'case01_callee_entry.py')
entry=importlib.util.module_from_spec(spec); spec.loader.exec_module(entry)

# Each is checked independently at its original PC.
BLOCKS=((0x12ae2,bytes.fromhex('f65009618280')),
        (0x12aec,bytes.fromhex('ddbf')),
        (0x12b00,bytes.fromhex('9305e0054800eff09fdfe1bf')),
        (0x12b1e,bytes.fromhex('9305a006cdb7')))


def run(image,mode,sp,saved_ra):
    if mode not in (0,1,2): raise ValueError('unsupported mode')
    def get(pc,n): return image[pc-0x8000:pc-0x8000+n]
    for pc,expected in BLOCKS:
        if get(pc,len(expected))!=expected: raise ValueError(f'instruction mismatch at {pc:#x}')
    if entry.calls.cj(0x12aec,get(0x12aec,2))!=0x12ae2: raise ValueError('zero-mode jump mismatch')
    if entry.calls.cj(0x12b0a,get(0x12b0a,2))!=0x12ae2: raise ValueError('return jump mismatch')
    if entry.calls.cj(0x12b22,get(0x12b22,2))!=0x12b04: raise ValueError('shared call jump mismatch')
    target=entry.calls.jal(0x12b06,get(0x12b06,4))
    if target!=0x128fe: raise ValueError('call target mismatch')
    sp &= 0xffffffff; saved_ra &= 0xffffffff
    second=None if mode==0 else (target,(sp+4)&0xffffffff,94 if mode==1 else 106,0x12b0a)
    return second,((sp+128)&0xffffffff,saved_ra)


def main():
    image=entry.calls.case.dispatch.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=entry.calls.case.dispatch.SHA: raise ValueError('APP identity mismatch')
    for sp in range(65536):
        for mode in (0,1,2):
            second,ret=run(image,mode,sp,0x1453c)
            want=None if mode==0 else (0x128fe,(sp+4)&0xffffffff,94 if mode==1 else 106,0x12b0a)
            if second!=want or ret!=((sp+128)&0xffffffff,0x1453c): raise ValueError('continuation mismatch')
    for sp in (0xffffff80,0xfffffffc,0xffffffff):
        for mode in (0,1,2):
            second,ret=run(image,mode,sp,0xffffffff)
            if ret!=((sp+128)&0xffffffff,0xffffffff) or (second and second[1]!=(sp+4)&0xffffffff): raise ValueError('wrap mismatch')
    mutations=0
    for pc,code in BLOCKS:
        for i in range(len(code)):
            bad=bytearray(image); bad[pc-0x8000+i]^=1
            try: run(bad,2,0x20000000,0x1453c)
            except ValueError: mutations+=1; continue
            raise ValueError('mutation accepted')
    print(f'PASS: 196608 selector/stack cases, 9 wrap cases, {mutations} byte mutations')
    print('After first call returns, mode 0 returns; modes 1/2 call 0x128fe(sp+4,94/106), then return if it returns.')
    print('Memory access, external callees and hardware are not executed.')

if __name__=='__main__': main()
