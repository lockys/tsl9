"""Abstract a4/a5 base flow over the closed original filter callee CFG.

Expressions are (constant,index coefficient), modulo 2^32. The index is the
value returned by the actual byte read, not the caller's earlier intended value.
This does not model memory, traps, interrupts, or MMIO behavior.
"""
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('alias',HERE/'filter_callee_alias.py')
alias=importlib.util.module_from_spec(spec); spec.loader.exec_module(alias)
MASK=0xffffffff
EXPECTED={
 0x18bb8:(0x40006600,0),0x18bca:(0x4000661c,0),0x18be0:(0x4000660c,0),
 0x18bf4:(0x40006640,8),0x18c00:(0x40006644,8),0x18c18:(0x40006604,0),
 0x18c30:(0x40006614,0),0x18c46:(0x4000661c,0),0x18c54:(0x40006600,0),
 0x18c6a:(0x4000660c,0),0x18c7e:(0x40006640,8),0x18c9e:(0x40006614,0),
}


def plus(a,b):
    if a is None or b is None: return None
    return ((a[0]+b[0])&MASK,(a[1]+b[1])&MASK)


def flow(image):
    _,_,_,edges=alias.audit.scan(image); alias.verify_stores(image)
    states={alias.audit.START:{(None,None)}}; pending=[alias.audit.START]; observed={}
    while pending:
        pc=pending.pop(); before=states[pc].copy()
        off=pc-0x8000; h=int.from_bytes(image[off:off+2],'little'); q=h&3
        width=4 if q==3 else 2; w=int.from_bytes(image[off:off+width],'little')
        for old in before:
            regs={14:old[0],15:old[1]}
            def get(reg): return regs.get(reg)
            if width==4:
                op=w&127; rd=(w>>7)&31; rs1=(w>>15)&31
                if op==0x23:
                    base,_,imm=alias.decode_store(w)
                    addr=plus(get(base),(imm&MASK,0))
                    observed.setdefault(pc,set()).add(addr)
                elif rd in regs and op in (0x03,0x13,0x33,0x37):
                    value=None
                    if op==0x37: value=(w&0xfffff000,0)
                    elif op==0x13 and (w>>12)&7==0:
                        imm=w>>20; imm=imm-4096 if imm&2048 else imm
                        value=plus(get(rs1),(imm&MASK,0))
                    elif op==0x03 and pc==0x18bae and rd==15 and rs1==10 and (w>>12)&7==4 and w>>20==10:
                        value=(0,1)
                    regs[rd]=value
            elif q==0 and h>>13==2:
                rd=8+((h>>2)&7)
                if rd in regs: regs[rd]=None
            elif q==1 and h>>13 in (0,2):
                rd=(h>>7)&31
                if rd in regs:
                    imm=((h>>2)&31)|(((h>>12)&1)<<5)
                    if imm&32: imm-=64
                    regs[rd]=(imm&MASK,0) if h>>13==2 else plus(regs[rd],(imm&MASK,0))
            elif q==1 and h>>13==4:
                rd=8+((h>>7)&7)
                if rd in regs: regs[rd]=None
            elif q==2 and h>>13==0:
                rd=(h>>7)&31
                if rd in regs:
                    amount=((h>>2)&31)|(((h>>12)&1)<<5)
                    if amount>=32: raise ValueError('unsupported shift')
                    v=regs[rd]; regs[rd]=None if v is None else ((v[0]<<amount)&MASK,(v[1]<<amount)&MASK)
            elif q==2 and h>>13==4 and h!=0x8082:
                rd=(h>>7)&31; rs2=(h>>2)&31
                if rd in regs:
                    regs[rd]=plus(get(rd),get(rs2)) if (h>>12)&1 else get(rs2)
            state=(regs[14],regs[15])
            for target in edges[pc]:
                targetset=states.setdefault(target,set())
                if state not in targetset: targetset.add(state); pending.append(target)
    if set(observed)!=set(EXPECTED): raise ValueError('store PCs mismatch')
    for pc,expression in EXPECTED.items():
        if observed[pc]!={expression}: raise ValueError(f'base flow mismatch {pc:x}: {observed[pc]}')
    return observed,states


def main():
    image=alias.audit.loop.calls.case.dispatch.IMAGE.read_bytes()
    observed,states=flow(image)
    union=alias.all_indices_stores()
    for pc,expressions in observed.items():
        base,factor=next(iter(expressions))
        for index in range(256):
            addr=(base+factor*index)&MASK
            word=alias.byte_set((addr,),4)
            if not word<=union: raise ValueError(f'full-byte bound mismatch {pc:x}')
            if index<14 and not word<=alias.writes(index): raise ValueError(f'bound mismatch {pc:x}')
    print(f'PASS: {len(states)} reachable instruction PCs, {len(observed)} store expressions, 3072 store/index checks')
    print('Full byte-index union validated for 0..255; narrower index-specific union validated for 0..13.')
    print('Symbolic base flow only; memory side effects, interrupts, faults and MMIO are not executed.')

if __name__=='__main__': main()
