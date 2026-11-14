"""Reference-only WCH candidate clock providers, never installed-ROM proof.

Each optional local carrier is hash-pinned; absent files are reported as SKIP.
The callback is a synthetic normal-return stub that preserves s0, sp, and the
saved stack words. Its result and the counter after callback are inputs.
"""
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MASK=0xffffffff
CANDIDATES=(
 ('v1.31','analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22',0x43520,0x20003230,0x200031b0,'b737002083a70723411122c406c6373400201304c41989c782975c483e9548c84848b240224441018280'),
 ('v1.40','analysis/wch-resident-candidate-2026-10-21/carrier/REFERENCE-CANDIDATE-ONLY-00040000-0006EC56.bin','b02cf8ec6829425a558887bd6bc10d28ae1f0e2e9e1850333f0bab6088e9e941',0x435ac,0x20003280,0x20003200,'b737002083a70728411122c406c6373400201304c41e89c782975c483e9548c84848b240224441018280'),
)

def run(code,expected,entry,callback_addr,counter_addr,ptr,before,after,increment,sp,ra,s0):
    if any(not 0<=x<=MASK for x in (ptr,before,after,increment,sp,ra,s0)): raise ValueError('RV32 input')
    # Each instruction is pinned before applying this bounded semantics.
    pcs=(0,4,8,10,12,14,18,22,24,26,28,30,32,34,36,38,40)
    sizes=(4,4,2,2,2,4,4,2,2,2,2,2,2,2,2,2,2)
    events=[]; pc=0; counter=before; new_sp=(sp-16)&MASK
    while True:
        if pc not in pcs: raise ValueError('invalid pc')
        i=pcs.index(pc); n=sizes[i]
        if code[pc:pc+n]!=expected[pc:pc+n]: raise ValueError('instruction mismatch')
        if pc==4: events.append(('read',callback_addr,4,ptr))
        elif pc==10: events.append(('write',(new_sp+8)&MASK,4,s0))
        elif pc==12: events.append(('write',(new_sp+12)&MASK,4,ra))
        elif pc==22 and not ptr: pc=32; continue
        elif pc==24:
            events.append(('call',ptr&~1,entry+26)); counter=after
        elif pc==26: events.append(('read',counter_addr,4,counter))
        elif pc==28: counter=(counter+increment)&MASK
        elif pc==30: events.append(('write',counter_addr,4,counter))
        elif pc==32: events.append(('read',counter_addr,4,counter))
        elif pc==34: events.append(('read',(new_sp+12)&MASK,4,ra))
        elif pc==36: events.append(('read',(new_sp+8)&MASK,4,s0))
        elif pc==40: return counter,sp,ra,s0,tuple(events)
        pc+=n

def check_candidate(item):
    name,path,digest,entry,callback,counter,hexbytes=item
    p=ROOT/path
    if not p.exists(): print(f'SKIP: {name} local reference carrier missing'); return False
    raw=p.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=digest: raise ValueError(f'{name}: carrier hash mismatch')
    if int.from_bytes(raw[0x7c:0x80],'little')!=entry: raise ValueError('slot target mismatch')
    expected=bytes.fromhex(hexbytes); code=raw[entry-0x40000:entry-0x40000+len(expected)]
    if code!=expected: raise ValueError('candidate instruction bytes mismatch')
    for i in range(65536):
        before=i; after=(i*65537)&MASK; delta=(MASK-i)&MASK
        for ptr in (0,0x1235):
            result,sp,ra,s0,events=run(code,expected,entry,callback,counter,ptr,before,after,delta,0x20001000,0x8908,0xabcdef01)
            want=((after+delta)&MASK) if ptr else before
            if (result,sp,ra,s0)!=(want,0x20001000,0x8908,0xabcdef01): raise ValueError('result mismatch')
            if any(e[0]=='call' for e in events)!=(ptr!=0): raise ValueError('call mismatch')
            if sum(e[0]=='write' and e[1]==counter for e in events)!=(1 if ptr else 0): raise ValueError('counter write mismatch')
    for i in range(len(code)):
        m=bytearray(code); m[i]^=1
        try: run(m,expected,entry,callback,counter,1,0,0,0,0x20001000,0x8908,0)
        except ValueError: continue
        raise ValueError(f'mutation not detected {i}')
    print(f'PASS: {name} slot {entry:#x}, 131072 synthetic cases, {len(code)} byte mutations')
    return True

def main():
    checked=sum(check_candidate(x) for x in CANDIDATES)
    print(f'Checked {checked}/2 optional reference candidates; no installed-ROM or hardware claim.')
if __name__=='__main__': main()
