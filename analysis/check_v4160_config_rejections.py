"""Offline init gate: APP call to first copy or APP rejection. Args: APP, V1.31, rasm2.
Synthetic config and peripheral; conditional on mapped reference code and Xwchc.
"""
from collections import Counter
from hashlib import sha256
from itertools import product
from pathlib import Path
import re
import subprocess
import sys


def check(ok, label):
    if not ok:
        raise ValueError(label)


def decode(app, rom, tool):
    code = {}
    ranges = [(app, 0x8000, 0x19ae6, 0x19af2),
              (rom, 0x40000, 0x43c7e, 0x43cc4), (rom, 0x40000, 0x43d50, 0x43d62),
              (rom, 0x20000000-0x270, 0x200004bc, 0x200004fa)]
    for image, base, lo, hi in ranges:
        raw = image[lo-base:hi-base]; pc = lo
        rows = subprocess.check_output([tool, '-a', 'riscv', '-b', '32', '-s', hex(lo), '-D', raw.hex()], text=True)
        for row in rows.splitlines():
            addr, n, h, op, *args = row.split(); n = int(n)
            check(int(addr, 16) == pc and bytes.fromhex(h) == raw[pc-lo:pc-lo+n], 'byte ledger')
            if pc == 0x43c90:
                check(h == '5a21', 'Xwchc halfword'); op, args = 'lhu', ['a4,4(a0)']
            code[pc] = n, op, ''.join(args).split(','); pc += n
        check(pc == hi, 'window boundary')
    return code


def run(code, slot, arena, size, first_diff, page, reader, writer):
    sp = 0x2000ff70; cfg = sp+16; ctrl = 0x4002420c
    r = dict(sp=sp, s0=123, s1=456, a5=0x40000); mem = {}; reads = []; status = []
    def put(p, w, v):
        for i in range(w): mem[p+i] = (v >> (8*i)) & 255
    def get(p, w): return sum(mem[p+i] << (8*i) for i in range(w))
    put(0x400a4, 4, slot); put(cfg, 4, arena); put(cfg+4, 2, size); put(ctrl, 4, 17)
    for d, v in [(8,page), (56,reader), (60,writer)]: put(cfg+d, 4, v)
    for i in range(6): put(cfg+24+i, 1, 254 if i == first_diff else 255)
    pc = 0x19ae6
    for _ in range(100):
        if pc == 0x43cc4 or pc == 0x19af0 and len(status) == 2: break
        if pc == 0x19aee or pc == 0x19af0: status.append(r['a0'])
        at = pc; n, op, x = code[pc]; pc += n; t = x[0]
        def val(s): return r[s] if s in r else int(s, 0)
        def addr(s):
            d, k = re.fullmatch(r'(-?\d+)\((\w+)\)', s).groups(); return (r[k]+int(d)) & 0xffffffff
        if op in ('lw','lbu','lhu','sw'):
            p = addr(x[1]); w = {'lw':4,'lhu':2,'lbu':1,'sw':4}[op]
            if op == 'sw': put(p,w,0 if t == 'zero' else r[t])
            else:
                r[t] = get(p,w)
                if cfg <= p < cfg+64: reads.append(p-cfg)
        elif op in ('li','lui','auipc','mv','addi','add','and'):
            v = val(x[1]); r[t] = (v if op in ('li','mv') else v << 12 if op == 'lui' else at+(v<<12) if op == 'auipc' else v & val(x[2]) if op == 'and' else v+val(x[2])) & 0xffffffff
        elif op in ('beqz','bnez','beq','bne'):
            y = 0 if op.endswith('z') else val(x[1]); take = (r[t] == y) == op.startswith('beq')
            if take: pc = val(x[-1])
        elif op == 'jalr':
            target = addr(t) if '(' in t else r[t]; r['ra'] = pc; pc = target & ~1
        elif op == 'ret': pc = r['ra'] & ~1
        elif op == 'j': pc = val(t)
        elif op != 'fence.i': raise ValueError(op)
    want = [0]; rc = 2
    if arena >> 16 == 0x2000:
        want.append(4)
        if size:
            want += list(range(24,30 if first_diff == 6 else 25+first_diff)); rc = 3
            if first_diff != 6:
                want.append(8); rc = 0
                if page:
                    want.append(56)
                    if reader: want.append(60)
                    if not reader or not writer: rc = 6
    check(reads == want and get(ctrl,4) == 17, 'configuration sampling order or peripheral restore')
    if rc: check((pc,status,r['sp'],r['s0'],r['s1']) == (0x19af0,[rc,rc],sp,123,456), 'rejection did not return to APP self-branch')
    else: check(pc == 0x43cc4 and not status, 'accepted prefix')
    return rc


if __name__ == '__main__':
    app, rom = (Path(p).read_bytes() for p in sys.argv[1:3])
    check([sha256(x).hexdigest() for x in (app,rom)] == ['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'], 'image identity')
    code = decode(app,rom,sys.argv[3]); slot = int.from_bytes(rom[164:168],'little')
    cases = product((0,0x1fffffff,0x20000000,0x2000ffff,0x20010000), (0,1), range(7), (0,1), (0,1), (0,1))
    counts = Counter(run(code,slot,*case) for case in cases)
    check(counts == {2:448,3:16,6:36,0:60}, 'fixture totals')
    print('PASS: 448 status-2, 16 status-3, 36 status-6 APP branches; 60 accepted prefixes')
