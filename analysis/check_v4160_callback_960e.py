"""0x960e: delayed settings callback, not an immediate Flash operation.
Run from repo root. Check APP instruction fields, not provider implementation.
"""
from hashlib import sha256
from pathlib import Path

b = Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()

def need(ok):
    if not ok: raise ValueError('APP evidence mismatch')

def word(pc):
    return int.from_bytes(b[pc-0x8000:pc-0x8000+4], 'little')

def signed(n, bits):
    return n - ((n >> (bits-1)) << bits)

def store(pc):
    w = word(pc)
    need(w & 127 == 35)
    return (w >> 12 & 7, w >> 15 & 31, w >> 20 & 31,
            signed((w >> 25 << 5) | (w >> 7 & 31), 12))

def pc_store(pc):
    w = word(pc); kind, base, src, off = store(pc+4)
    need(w & 127 == 23 and w >> 7 & 31 == base)
    return kind, src, (pc + (w & 0xfffff000) + off) & 0xffffffff

need(sha256(b).hexdigest() == '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
need([pc_store(pc) for pc in (0x942c,0x9434,0x9616,0x93c0,0x93c8,0x93d0)] == [
    (2,0,0x2000becc),(2,0,0x2000bec8),(2,10,0x2000becc),
    (0,0,0x2000bec2),(0,0,0x2000bec1),(2,0,0x2000bebc)])
# Replay only the straight-line LI/SH descriptor construction, ignoring the frame reload.
regs = {0:0}; writes = []
for pc in (0x9620,0x9624,0x9628,0x962c,0x9630,0x9634,0x963a,0x963e,0x9642,0x9646,0x964a):
    w = word(pc)
    if w & 0xfffff == 0x793: regs[15] = signed(w >> 20,12)
    else:
        kind,base,src,off = store(pc); need((kind,base)==(1,10)); writes.append((off,regs[src]))
need(writes == [(0,1165),(2,130),(6,1465),(4,0),(8,150),(10,0),(12,0)])
need(b[0x143e:0x1454].hex() == '19453305a402b70704002244b24003a3070741010283')
need(b[0x13d8:0x13ee].hex() == 'b70700402392074203d70740136717002390e7408280')
print('PASS: six PC-relative stores; seven ordered descriptor writes; request-size and MMIO tail bytes')
