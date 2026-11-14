"""Bounded first-call projection of the 0x12ad0 selector.

No callee is executed. Fixed instruction bytes guard the manually transcribed
projection; JAL targets and PC-relative data addresses are decoded separately.
"""
import hashlib
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('calls',HERE/'case01_calls.py')
calls=importlib.util.module_from_spec(spec); spec.loader.exec_module(calls)
START=0x12ad0
CODE=bytes.fromhex('197186de8547630cf50019c589476307f502f65009618280eff07febddbf977500009385a5211306e0054800ef70400f9305e0054800eff09fdfe1bf977500009385c5251306a0064800ef70600d')


def branch(pc,code):
    w=int.from_bytes(code,'little')
    if len(code)!=4 or w&127!=0x63: raise ValueError('not branch')
    imm=((w>>31&1)<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1)
    return pc+(imm-8192 if imm&4096 else imm)


def data_address(pc,code):
    if len(code)!=8: raise ValueError('bad address instructions')
    upper=int.from_bytes(code[:4],'little'); lower=int.from_bytes(code[4:],'little')
    if upper&0xfff!=0x597 or lower&0xfffff!=0x58593: raise ValueError('bad auipc/addi operands')
    low=lower>>20; low=low-4096 if low&2048 else low
    return (pc+(upper&0xfffff000)+low)&0xffffffff


def project(image,value,sp,ra):
    code=image[START-0x8000:START-0x8000+len(CODE)]
    if code!=CODE: raise ValueError('instruction mismatch')
    sp=(sp-128)&0xffffffff
    if branch(0x12ad6,code[6:10])!=0x12aee or branch(0x12ade,code[14:18])!=0x12b0c: raise ValueError('branch target mismatch')
    if value==0:
        return (sp,(sp+124)&0xffffffff,ra,0x1299e,None)
    if value in (1,2):
        pc=(0x12aee if value==1 else 0x12b0c); off=pc-START
        addr=data_address(pc,code[off:off+8]); target=calls.jal(pc+14,code[off+14:off+18])
        return (sp,(sp+124)&0xffffffff,ra,target,((sp+4)&0xffffffff,addr,94 if value==1 else 106))
    return (sp,(sp+124)&0xffffffff,ra,None,None)


def main():
    image=calls.case.dispatch.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=calls.case.dispatch.SHA: raise ValueError('APP identity mismatch')
    for value in range(65536):
        sp=0x20001000; ra=0x1453c
        out=project(image,value,sp,ra)
        want=(sp-128,sp-4,ra,0x1299e,None) if value==0 else ((sp-128,sp-4,ra,0x19bf0,(sp-124,0x19d08 if value==1 else 0x19d68,94 if value==1 else 106)) if value in (1,2) else (sp-128,sp-4,ra,None,None))
        if out!=want: raise ValueError(f'projection mismatch: {value}: {out}')
    for pc in range(len(CODE)):
        bad=bytearray(image); bad[START-0x8000+pc]^=1
        try: project(bad,2,0x20001000,0x1453c)
        except ValueError: continue
        raise ValueError(f'mutation accepted {START+pc:#x}')
    for sp in (0,1,127,128,0xffffffff):
        out=project(image,2,sp,0xdeadbeef)
        if out[0]!=(sp-128)&0xffffffff or out[1]!=(sp-4)&0xffffffff or out[4][0]!=(sp-124)&0xffffffff: raise ValueError('stack wrap mismatch')
    print(f'PASS: 65536 selector values, 5 stack boundaries, {len(CODE)} instruction-byte mutations')
    print('a0=0 first calls 0x1299e; a0=2 first calls 0x19bf0(sp+4,0x19d68,106).')
    print('Fixed encoding projection only; memory access, callees, continued execution and hardware unverified.')

if __name__=='__main__': main()
