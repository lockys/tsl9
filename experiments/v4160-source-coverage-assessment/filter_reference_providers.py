"""Identify two optional public reference provider bodies, not installed ROM.

Flash-to-RAM offsets are conditional on the candidate startup copies, not proof
that startup completed. This checks identity only; it does not execute code.
"""
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CANDIDATES=(
 ('V1.31','analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22',0x405a2,0x4060c),
 ('V1.40','analysis/wch-resident-candidate-2026-10-21/carrier/REFERENCE-CANDIDATE-ONLY-00040000-0006EC56.bin','b02cf8ec6829425a558887bd6bc10d28ae1f0e2e9e1850333f0bab6088e9e941',0x405e2,0x4064c),
)
COPY=bytes.fromhex('b747024003a7c72023a607200f10000001c599c1814711e6b747024023a6e7208280b386f50003c80600b306f500850723800601e317f6fec5b7')
FILL=bytes.fromhex('374702408327c720232607200f10000001c53307c50011e6374702402326f72082800505a30fb5fee31de5fef5b7')

def check(raw,digest,copy,fill):
    if hashlib.sha256(raw).hexdigest()!=digest: raise ValueError('carrier hash')
    def at(pc,n): return raw[pc-0x40000:pc-0x40000+n]
    if at(0x40048,8)!=bytes.fromhex('9c03002032030020'): raise ValueError('slots')
    if at(copy,len(COPY))!=COPY or at(fill,len(FILL))!=FILL: raise ValueError('body')
    # In both retained loaders, offset between the two RAM entries equals
    # the offset between their mapped flash source addresses.
    if fill-copy != 0x2000039c-0x20000332: raise ValueError('mapping offset')

def main():
    count=0
    for name,path,digest,copy,fill in CANDIDATES:
        p=ROOT/path
        if not p.exists(): print(f'SKIP {name}: local reference unavailable'); continue
        raw=p.read_bytes(); check(raw,digest,copy,fill); count+=1
        for address in (0x40048,0x4004c,*range(copy,copy+len(COPY)),*range(fill,fill+len(FILL))):
            mutant=bytearray(raw); mutant[address-0x40000]^=1
            try: check(mutant,digest,copy,fill)
            except ValueError: continue
            raise ValueError(f'mutation accepted at {address:#x}')
        print(f'PASS {name}: slots and mapped 58-byte copy / 46-byte fill bodies; 106 byte mutations rejected by carrier hash')
    if not count: raise SystemExit('No reference carrier available')
    print('Reference candidates only: installed slots, startup, provider completion and hardware remain unverified.')
if __name__=='__main__': main()
