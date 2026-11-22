"""Bounded V1.31 timer traversal. Optional clock sample models a side-effect-free return."""
from collections import ChainMap


def trace(code, ram, regs, sample=None):
    m = ChainMap({}, ram)
    r = dict(regs, ra=0x20000874, s0=0x20003514, zero=0)
    pc = 0x200004fa
    stores, calls = [], []
    mask = 0xffffffff
    def val(k): return r[k] if k in r else int(k, 0)
    def address(arg):
        d, k = arg[:-1].split('(')
        return (r[k]+int(d)) & mask
    for _ in range(250):
        if pc == 0x20000874: return ('return', pc), stores, calls, m
        at = pc
        n, op, args = code[pc]; pc += n
        t = args[0]
        if op in ('lw','lbu','sw','lhu'):
            p = address(args[1]); w = {'lw':4,'sw':4,'lbu':1,'lhu':2}[op]
            if op == 'sw':
                stores.append((at,p,r[t]))
                m.update({p+i:(r[t]>>(8*i))&255 for i in range(w)})
            else: r[t] = sum(m[p+i]<<(8*i) for i in range(w))
        elif op in ('li','mv','lui','auipc','addi','sub','add'):
            x = val(args[1]); y = val(args[2]) if len(args)>2 else 0
            r[t] = ((x<<12) + (at if op=='auipc' else 0) if op in ('lui','auipc') else x-y if op=='sub' else x+y)&mask
        elif op in ('beqz','bnez','bleu','bltu'):
            take = (r[t]==0 if op=='beqz' else r[t]!=0 if op=='bnez' else r[t]<=val(args[1]) if op=='bleu' else r[t]<val(args[1]))
            if take: pc = val(args[-1])
        elif op in ('jalr','jal'):
            dest = ((address(t) if '(' in t else val(t))&~1) if op=='jalr' else val(args[-1]); r['ra']=pc
            calls.append((at,dest))
            if at==0x20000560 and sample is not None: r['a0']=sample
            else: return ('call',dest), stores, calls, m
        elif op=='j': pc=val(t)
        elif op=='ret': pc=r['ra']&~1
        else: raise ValueError((hex(at), op))
    raise ValueError('timer trace exceeded bound')
