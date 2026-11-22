"""V1.31 getter and third role allocation request from the second-record join.

Uses the caller's decoded instruction map and inherited RAM; no allocator return
is injected. memory maps byte addresses to bytes. Stops at allocator entry.
The local driver supplied 32 inherited null and 32 successful second returns:
all 64 yielded size 60, tag 0x4c06. Replacing COUNT only by 0, 1 or 255 in
separate controls yielded sizes 0, 12 or 3060. Not device observations.
"""

COUNT = 0x200033b4


def request(code, regs, memory):
    pc = 0x4efd8
    if regs['ra'] != 0x4db88:
        raise ValueError('wrong getter continuation')
    r = regs.copy()
    reads = []
    for _ in range(16):
        if pc == 0x20000040:
            if reads != [(0x4efdc, COUNT)] or (
                r['a0'], r['a1'], r['ra']
            ) != (12 * memory[COUNT], 0x4c06, 0x4dba0):
                raise ValueError('third request or read set')
            return r
        at = pc
        width, op, args = code[pc]
        pc += width
        t = args[0]
        if op in ('lbu', 'jalr'):
            off, base = args[-1][:-1].split('(')
            dest = (int(off) + r[base]) & 0xffffffff
            if op == 'lbu':
                reads.append((at, dest))
                r[t] = memory[dest]
            else:
                r['ra'], pc = pc, dest & ~1
        elif op == 'ret':
            pc = r['ra'] & ~1
        elif op in ('lui', 'auipc'):
            r[t] = ((int(args[1], 0) << 12) + (at if op == 'auipc' else 0)) & 0xffffffff
        elif op == 'li':
            r[t] = int(args[1], 0)
        elif op == 'mul':
            r[t] = (r[args[1]] * r[args[2]]) & 0xffffffff
        elif op in ('addi', 'slli', 'srli'):
            a, b = r[args[1]], int(args[2], 0)
            if op == 'addi': r[t] = (a+b) & 0xffffffff
            elif op == 'slli': r[t] = (a << (b & 31)) & 0xffffffff
            else: r[t] = a >> (b & 31)
        else:
            raise ValueError((hex(at), op))
    raise ValueError('getter did not reach allocation')
