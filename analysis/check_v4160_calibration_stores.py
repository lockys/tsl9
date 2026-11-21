"""Offline: supply decoded APP, V1.31 reference carrier, and rasm2 executable."""
import hashlib
import re
import subprocess
import sys
from collections import deque
from pathlib import Path


def ck(x):
    if not x:
        raise ValueError('calibration ledger mismatch')


a, b = (Path(p).read_bytes() for p in sys.argv[1:3])
ck(hashlib.sha256(a).hexdigest() == '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
ck(hashlib.sha256(b).hexdigest() == '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')


def decode(lo, hi):
    raw = a[lo-0x8000:hi-0x8000]
    text = subprocess.check_output([sys.argv[3], '-a', 'riscv', '-b', '32', '-s', hex(lo), '-D', raw.hex()], text=True)
    rows = {}; p = lo
    for line in text.splitlines():
        addr, n, h, op, *tail = line.split(); n = int(n)
        ck(int(addr, 16) == p and n in (2, 4) and len(h) == 2*n and bytes.fromhex(h) == raw[p-lo:p-lo+n])
        rows[p] = (n, op, ''.join(tail).split(',')); p += n
    ck(p == hi)
    return rows


helper = decode(0x191c6, 0x19220)
ck(all(op in {'lui','lhu','slli','srli','bne','beq','or','ret'} for _,op,_ in helper.values()))
ck(all(args[0] in {'a0','a1','a2','a3','a4','a5'} for _,op,args in helper.values() if op not in {'beq','bne','ret'}))
rows = decode(0x1929a, 0x196c4)


def ledger(entry_sp):
    states = {}; todo = deque(); stores = {}
    def offer(p, state):
        ck(p in rows)
        merged = state if p not in states else {k:v for k,v in states[p].items() if state.get(k) == v}
        if states.get(p) != merged:
            states[p] = merged; todo.append(p)
    offer(0x1929a, {'sp':entry_sp})
    while todo:
        p = todo.popleft(); s = states[p].copy(); n,op,t = rows[p]; dst = t[0]
        if op in {'sb','sw','sh'}:
            m = re.fullmatch(r'(-?\d+)\((\w+)\)', t[1]); ck(m and m[2] in s)
            stores[p] = (s[m[2]]+int(m[1]), {'sb':1,'sh':2,'sw':4}[op], m[2]=='sp')
        elif op == 'jal':
            ck(t == ['ra','0x191c6']); s.pop('ra',None)
            for k in ('a0','a1','a2','a3','a4','a5'): s.pop(k,None)
        elif op == 'ret': continue
        elif op == 'j': offer(int(dst,0),s); continue
        elif op in {'beq','beqz','bgez','ble','blez','blt','bltz'}: offer(int(t[-1],0),s)
        elif op in {'lui','li'}: s[dst] = int(t[1],0) << (12 if op=='lui' else 0)
        elif op == 'addi' and t[1] in s: s[dst] = (s[t[1]] + int(t[2],0)) & 0xffffffff
        elif op == 'mv' and t[1] in s: s[dst] = s[t[1]]
        else:
            ck(op in {'add','addi','and','andi','div','lbu','lhu','lw','mul','mv','or','ori','sll','slli','srai','srli','sub'}); s.pop(dst,None)
        offer(p+n,s)
    ck(len(states)==len(rows) and len(stores)==50)
    return list(stores.values())


ck(a[0xe88:0xe8a].hex()=='0111' and a[0x11b16:0x11b18].hex()=='4111' and a[0x11b56:0x11b58].hex()=='0111' and b[0x3f46:0x3f48].hex()=='0111')
for extra in (0,32):
    sp = 0x20010000-32-16-32-extra
    w = ledger(sp); stack = [(x,n) for x,n,k in w if k]
    io = {(x,n) for x,n,k in w if not k}
    ck(len(stack)==14 and all(sp-80<=x and x+n<=sp for x,n in stack))
    ck(io=={(0x40022049,1),(0x4002204f,1),(0x4002204c,2),(0x40022036,2)})
    ck(not any(x<=0x20004184<x+n for x,n,_ in w))
    print(f'PASS: entry SP={sp:#x}; 14 stack and 36 MMIO store sites; task byte excluded')
