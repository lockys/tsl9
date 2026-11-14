"""Static register-destination audit of pinned WCH reference copy bodies.

Only the exact candidate instruction sequence is recognized. Not execution.
"""
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('providers',HERE/'filter_reference_providers.py')
providers=importlib.util.module_from_spec(spec); spec.loader.exec_module(providers)


def destinations(code):
    if code!=providers.COPY: raise ValueError('unrecognized copy code')
    kinds=('lui','lw','sw','fence','c.beqz','c.beqz','c.li','c.bnez','lui','sw','c.jr','add','lbu','add','c.addi','sb','bne','c.j')
    out=[]; offset=0
    for kind in kinds:
        h=int.from_bytes(code[offset:offset+2],'little'); size=4 if h&3==3 else 2
        if size==4:
            w=int.from_bytes(code[offset:offset+4],'little')
            if kind in ('lui','lw','add','lbu'): out.append((offset,(w>>7)&31))
        elif kind in ('c.li','c.addi'): out.append((offset,(h>>7)&31))
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
        code=raw[copy-0x40000:copy-0x40000+len(providers.COPY)]
        rows=destinations(code)
        if rows!=[(0,15),(4,14),(20,15),(24,15),(34,13),(38,16),(42,13),(46,15)]: raise ValueError('destination mismatch')
        if set(r for _,r in rows)!={13,14,15,16}: raise ValueError('clobber mismatch')
        for i in range(len(code)):
            mutated=bytearray(code); mutated[i]^=1
            try: destinations(mutated)
            except ValueError: continue
            raise ValueError('mutated byte accepted')
        print(f'PASS {name}: 18 instructions, direct destinations a3/a4/a5/a6, {len(code)} byte mutations rejected')
        checked+=1
    if not checked: raise SystemExit('No candidate carrier available')
    print('SP/s0/s1/a0 are not direct destinations; faults, aliasing, interrupts, installed provider and execution remain unknown.')
if __name__=='__main__': main()
