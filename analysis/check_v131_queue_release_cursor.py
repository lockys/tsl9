"""Normal queue completion: characterize header selection, not allocation provenance.
Run with the V1.31 reference carrier used by check_v131_cmd6_queue_pop.py.
"""
import runpy
from pathlib import Path
q = runpy.run_path(str(Path(__file__).with_name('check_v131_cmd6_queue_pop.py')))
rom, raw, ck = q['rom'], q['raw'], q['ck']
for p in (0x5981c, 0x615f8):
    ck(raw(p, 8).hex() == 'c843136707f0baa7' and q['target'](p+8) == 0x20000110)

def field(pc):
    i = 0x270 + pc - 0x20000000
    return int.from_bytes(rom[i:i+4], 'little')

def branch(pc, regs):
    w = field(pc); ck(w & 127 == 99)
    a, b = regs[w >> 15 & 31], regs[w >> 20 & 31]
    taken = {6: a < b, 7: a >= b}[w >> 12 & 7]
    delta = ((w >> 31) << 12 | (w >> 7 & 1) << 11 | (w >> 25 & 63) << 5 | (w >> 8 & 15) << 1)
    return pc + (q['sx'](delta, 13) if taken else 4)

ck(field(0x20000140) == 0x0007a883 and field(0x2000014c) == 0x00878713)
ck(field(0x20000178) == 0x00079323)  # sh zero,6(a5), not relative to a0
cases = 0
for size in (12, 16, 20, 24, 32, 64):
    h = 0x20005000; base = h+8; nxt = base+size
    for incoming in range(base, nxt-12+1):
        # node+4 initially incoming-2, first partial adds 2, completed copies add 12.
        end = incoming+12
        regs = {10:end, 15:h, 17:nxt, 14:base, 6:nxt+8}
        for pc in (0x2000013c, 0x20000144, 0x20000148, 0x20000150):
            ck(branch(pc, regs) == pc+4)
        cases += 1
print(f'PASS: 2 release call sites; {cases} nominal cursor placements including equality at next header; selected header retained in a5')
