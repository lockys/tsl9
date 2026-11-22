"""Check the V1.31 role registration tail on a decoded map and inherited state.
No hooks or hardware. The optional occupied-prefix controls use a RAM overlay.
"""
from collections import ChainMap

TABLE = 0x20003358
HANDLER = 0x4d916


def trace(code, registers, memory, occupied=0):
    if not 0 <= occupied <= 12:
        raise ValueError('table capacity')
    r = registers.copy()
    m = ChainMap({}, memory)
    def word(p): return int.from_bytes(bytes(m[p+i] for i in range(4)), 'little')
    def store(p, v): m.update({p+i: b for i,b in enumerate(v.to_bytes(4, 'little'))})
    def address(arg):
        off, base = arg[:-1].split('(')
        return (r[base]+int(off)) & 0xffffffff
    if any(word(TABLE+4*i) for i in range(12)):
        raise ValueError('expected inherited empty table')
    for i in range(occupied): store(TABLE+4*i, HANDLER)
    sp = r['sp']; pc = 0x4dbc2; reads = []; writes = []
    for _ in range(128):
        if pc == 0x6dd2e: break
        width, op, x = code[pc]; pc += width; t = x[0]
        if op == 'lw':
            p = address(x[1]); reads.append(p); r[t] = word(p)
        elif op == 'sw':
            p = address(x[1]); writes.append((p,r[t])); store(p,r[t])
        elif op == 'ret': pc = r['ra'] & ~1
        elif op == 'j': pc = int(t,0)
        elif op in ('bne','bnez'):
            if r[t] != (r[x[1]] if op=='bne' else 0): pc = int(x[-1],0)
        elif op == 'li': r[t] = int(x[1],0)
        elif op == 'lui': r[t] = int(x[1],0)<<12
        elif op in ('addi','add','slli'):
            a = r[x[1]]; b = r[x[2]] if op=='add' else int(x[2],0)
            r[t] = ((a<<b) if op=='slli' else a+b) & 0xffffffff
        else: raise ValueError(('unexpected instruction',op))
    else: raise ValueError('no caller return')
    slots = [TABLE+4*i for i in range(min(occupied+1,12))]
    if reads != [sp+i for i in (40,44,36,32,28,24)] + slots:
        raise ValueError('unexpected data read')
    if writes != ([(TABLE+4*occupied,HANDLER)] if occupied<12 else []):
        raise ValueError('unexpected callback store')
    if r['a0'] != (0 if occupied<12 else 19) or r['sp'] != sp+48:
        raise ValueError('registration return')
    return r['a0']
