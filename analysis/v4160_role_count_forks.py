"""Bounded V1.31 count gate; no default for missing RAM and no allocator emulation."""
C = 0x20003350
MASK = 0xffffffff


def gate(code, entry, memory):
    regs = entry.copy()
    pc = 0x4daf6
    reads = []
    for _ in range(11):
        if pc in (0x4db3e, 0x20000040):
            return pc, regs, reads
        width, op, args = code[pc]
        at = pc
        pc += width
        t = args[0]
        if op == 'lbu' or op == 'jalr':
            off, reg = args[-1][:-1].split('(')
            addr = (regs[reg] + int(off, 0)) & MASK
            if op == 'lbu':
                reads.append(addr)
                regs[t] = memory[addr]
            else:
                regs['ra'], pc = pc, addr & ~1
        elif op == 'beqz':
            if regs[t] == 0:
                pc = int(args[1], 0)
        elif op in ('auipc', 'lui'):
            regs[t] = ((at if op == 'auipc' else 0) + (int(args[1], 0) << 12)) & MASK
        elif op in ('slli', 'addi'):
            a, b = regs[args[1]], int(args[2], 0)
            regs[t] = ((a << (b & 31)) if op == 'slli' else a + b) & MASK
        else:
            raise ValueError((hex(at), op))
    raise ValueError('unexpected count gate boundary')


def verify(code, regs, mem):
    from collections import ChainMap
    if C in mem or C+1 in mem:
        raise ValueError('fixture has count evidence; do not shadow it')
    try:
        gate(code, regs, mem)
    except KeyError as exc:
        if exc.args != (C,):
            raise
    else:
        raise ValueError('missing count did not stop the gate')
    for n in range(256):
        pc, r, reads = gate(code, regs, ChainMap({C:n}, mem))
        if reads != [C] or pc != (0x20000040 if n else 0x4db3e):
            raise ValueError(('count gate', n, pc, reads))
        if n and (r['a0'], r['a1'], r['ra']) != (16*n, 0x4c04, 0x4db18):
            raise ValueError(('allocation arguments', n))
