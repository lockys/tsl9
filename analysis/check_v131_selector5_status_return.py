"""Post-rejection return flow only. Args: APP, V1.31 reference, rasm2.
Execute the real return/branch instructions; nested calls are not executed.
Successful stack accesses and intact caller frames assumed, no device I/O.
"""
from pathlib import Path
import runpy

g = runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
for lo, hi in [(0x4324c,0x4325a),(0x4dfdc,0x4dfe0),(0x4dffc,0x4e000),
               (0x4dfa8,0x4dfb8),(0x4e23a,0x4e240),(0x4e224,0x4e226),
               (0x4e33c,0x4e34c)]:
    g['window'](g['b'],0x40000,lo,hi)
code = g['code']

def check(ok):
    if not ok: raise ValueError('selector-5 return flow mismatch')

def run(pc, stops, regs, mem):
    for _ in range(64):
        if pc in stops: return pc
        n, op, x = code[pc]; pc += n; d = x[0]
        if op == 'li': regs[d] = int(x[1],0)
        elif op == 'mv': regs[d] = regs[x[1]]
        elif op == 'addi': regs[d] = regs[x[1]] + int(x[2],0)
        elif op == 'lw':
            off, base = x[1][:-1].split('('); regs[d] = mem[regs[base]+int(off)]
        elif op == 'ret': pc = regs['ra'] & ~1
        elif op == 'j': pc = int(d,0)
        elif op == 'jal': regs['ra'],pc = pc,int(x[-1],0)
        elif op in ('bnez','beqz'):
            if (regs[d]==0) == (op=='beqz'): pc = int(x[-1],0)
        else: raise ValueError(op)
    raise ValueError('step limit')

def case(sp, parser, saved):
    r = dict(sp=sp,a0=parser); mem = {}
    check(run(0x4e23a,{0x4df54},r,mem)==0x4df54 and r['ra']==0x4e23e)
    mem.update({sp-64+off:v for off,v in [(60,r['ra']),(56,1),(52,2),(48,3),(44,4)]})
    r['sp']-=64
    dest=run(0x4dfdc,{0x4dfe0,0x4dfa8},r,mem)
    check(r['s1']==parser)
    if parser==0:
        check(dest==0x4dfe0)
        # Assume record enabled; move to caller's actual JAL. Supply helper's frame
        # at its post-copy epilogue, then send routine's frame after its nested release.
        check(run(0x4dffc,{0x4e2ee},r,mem)==0x4e2ee and r['ra']==0x4dffe)
        r['sp']-=48; base=r['sp'];mem.update({base+44:r['ra'],base+40:1,base+36:saved})
        r.update(s0=0x20005000,s1=255)
        check(run(0x4e33c,{0x43208},r,mem)==0x43208 and (r['a0'],r['a1'],r['s1'])==(255,0x20005000,saved))
        r['sp']-=16;base=r['sp'];mem.update({base+12:r['ra'],base+8:1,base+4:r['s1'],base:3})
        check(run(0x4324c,{0x4dffe},r,mem)==0x4dffe and r['a0']==3)
        check(run(0x4dffe,{0x4dfa8},r,mem)==0x4dfa8)
    else: check(dest==0x4dfa8)
    want=parser or saved
    check(run(0x4dfa8,{0x4e23e},r,mem)==0x4e23e and (r['sp'],r['a0'])==(sp,want))
    check(run(0x4e23e,{0x4e226,0x4e22c},r,mem)==(0x4e226 if want else 0x4e22c))

for sp in (0x2000ff80,0x2000ffc0):
    for p in range(256): case(sp,p,0)
    case(sp,0,91) # deliberately changed saved s1; outer branch changes despite inner 3
print('PASS: 2 rejection returns (inner 3 -> outer 0), 510 prior nonzero exits, 2 changed-frame controls')
