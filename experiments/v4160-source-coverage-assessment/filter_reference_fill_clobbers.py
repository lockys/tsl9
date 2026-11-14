"""Audit register destinations in the pinned reference fill leaf.

Only this exact 46-byte code sequence is recognized. This static instruction
projection does not execute a provider, memory access, or hardware.
"""
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('providers',HERE/'filter_reference_providers.py')
providers=importlib.util.module_from_spec(spec); spec.loader.exec_module(providers)


def destinations(code):
    if code!=providers.FILL: raise ValueError('unrecognized fill code')
    # Lengths/operations are the complete 14-instruction candidate CFG, including
    # the loop after RET. Registers are extracted from instruction fields.
    kinds=('lui','lw','sw','fence','c.beqz','add','c.bnez','lui','sw','c.jr','c.addi','sb','bne','c.j')
    out=[]; offset=0
    for kind in kinds:
        h=int.from_bytes(code[offset:offset+2],'little'); size=4 if h&3==3 else 2
        if size==4:
            w=int.from_bytes(code[offset:offset+4],'little')
            if kind in ('lui','lw','add'): out.append((offset,(w>>7)&31))
        elif kind=='c.addi': out.append((offset,(h>>7)&31))
        elif kind not in ('c.beqz','c.bnez','c.jr','c.j'): raise ValueError('unexpected compressed instruction')
        offset+=size
    if offset!=len(code): raise ValueError('instruction coverage')
    return out


def main():
    checked=0
    for name,path,digest,copy,fill in providers.CANDIDATES:
        p=providers.ROOT/path
        if not p.exists(): print(f'SKIP {name}'); continue
        raw=p.read_bytes(); providers.check(raw,digest,copy,fill)
        code=raw[fill-0x40000:fill-0x40000+len(providers.FILL)]
        rows=destinations(code)
        if rows!=[(0,14),(4,15),(18,14),(24,14),(34,10)]: raise ValueError('destination mismatch')
        if set(r for _,r in rows)!={10,14,15}: raise ValueError('clobber mismatch')
        for i in range(len(code)):
            mutated=bytearray(code); mutated[i]^=1
            try: destinations(mutated)
            except ValueError: continue
            raise ValueError('mutated byte accepted')
        print(f'PASS {name}: 14 instructions, direct destinations a0/a4/a5, {len(code)} bytes mutations rejected')
        checked+=1
    if not checked: raise SystemExit('No candidate carrier available')
    print('SP/s0/s1 are not direct destinations; faults, aliasing, interrupts, installed provider and execution remain unknown.')
if __name__=='__main__': main()
