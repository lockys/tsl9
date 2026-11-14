"""Conditional descriptor fields and callee route for one filter iteration.

Combines separately decoded caller events and original callee CFG; all reads
must succeed, no intervening writes/interrupts occur, and descriptor bytes must
not alias callee stores. It is not a CPU or MMIO emulator.
"""
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('flow',HERE/'filter_callee_baseflow.py')
flow=importlib.util.module_from_spec(spec); spec.loader.exec_module(flow)
A=flow.alias; MASK=0xffffffff


def half(mem,addr): return sum(mem[(addr+i)&MASK]<<(8*i) for i in range(2))
def word(mem,addr): return sum(mem[(addr+i)&MASK]<<(8*i) for i in range(4))


def describe(image,sp,values,index):
    if not 0<=index<14: raise ValueError('index out of range')
    if any(A.classify_all(sp)): raise ValueError('callee stores may alias descriptor or source')
    source=(sp+32)&MASK
    mem={(source+2*i+j)&MASK:(x>>(8*j))&255 for i,x in enumerate(values) for j in range(2)}
    result=A.audit.loop.step(image,mem,sp,source,index,1,1)
    descriptor=(sp+12)&MASK
    # Independently decoded branch operands and targets anchored to exact bytes.
    _,_,_,edges=A.audit.scan(image)
    expected={0x18bd2:(0x18bd4,0x18c5a),0x18c10:(0x18c12,0x18c8a),
              0x18c28:(0x18c2a,0x18c92),0x18c38:(0x18c3c,0x18c4a)}
    if any(edges[pc]!=v for pc,v in expected.items()): raise ValueError('branch target mismatch')
    if [image[pc-0x8000:pc-0x8000+n] for pc,n in ((0x18bd2,2),(0x18c10,2),(0x18c28,2),(0x18c38,4))]!=[bytes.fromhex(x) for x in ('c1e5','2def','2de7','6319f700')]: raise ValueError('branch operand mismatch')
    fields=tuple(half(mem,descriptor+2*i) for i in range(4))
    fifo=half(mem,descriptor+8); number=mem[(descriptor+10)&MASK]; mode=mem[(descriptor+11)&MASK]
    scale=mem[(descriptor+12)&MASK]; activation=word(mem,descriptor+16)
    # These outcomes are conditional on the unmodified descriptor, not a
    # claim that arbitrary MMIO reads or writes were executed.
    path=(edges[0x18bd2][int(scale!=0)],edges[0x18c10][int(mode!=0)],
          edges[0x18c28][int(fifo!=0)],edges[0x18c38][int(activation!=1)])
    return fields,fifo,number,mode,scale,activation,path,result[3:5]


def main():
    image=A.audit.loop.calls.case.dispatch.IMAGE.read_bytes(); flow.flow(image)
    expected_path=(0x18bd4,0x18c8a,0x18c2a,0x18c3c)
    # Repeating the CFG audit per input is expensive; use a representative
    # cross-product, plus independent exhaustive halfword arithmetic below.
    checks=0
    for index in range(14):
        for value in (0,1,0x7ff,0x800,0xffff,0x1234,0xfedc):
            values=(value,(value+1)&65535,value^65535,(value*7)&65535)
            fields,fifo,number,mode,scale,activation,path,regs=describe(image,0x20001000,values,index)
            if fields!=tuple((v<<5)&65535 for v in values) or (fifo,number,mode,scale,activation)!=(0,index,1,0,1): raise ValueError('descriptor mismatch')
            if path!=expected_path or regs!=(0x20001028,index+1): raise ValueError('path mismatch')
            checks+=1
    # Field projection is a 16-bit shift; verify exhaustive input domain.
    for value in range(65536):
        if ((value<<5)&65535)!=((value&0x7ff)*32): raise ValueError('shift identity mismatch')
    for sp in (0x40006620,0x40006e00):
        try: describe(image,sp,(1,2,3,4),0)
        except ValueError as exc:
            if str(exc)!='callee stores may alias descriptor or source': raise
        else: raise ValueError('unsafe alias accepted')
    print(f'PASS: {checks} descriptor/route cases, 65536 shift identities, two alias rejections')
    print('When descriptor remains stable: scale=0, mode=1, fifo=0, activation=1.')
    print('Conditional CFG route, not full callee execution, physical MMIO or reachability proof.')

if __name__=='__main__': main()
