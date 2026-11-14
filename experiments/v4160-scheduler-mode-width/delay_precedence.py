"""Compare zero/nonzero-delay route precedence at synthetic stable table boundaries.

The zero-delay scan and nonzero-delay match scan are separate bounded fixed-
encoding projections. Their composition is not continuous CPU execution.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
z=load('z',HERE/'zero_delay_scan.py'); m=load('m',HERE/'match_scan.py'); ins=load('ins',HERE/'zero_delay_insert.py'); upd=load('upd',HERE/'match_update.py')


def branch(image,delay):
    h=int.from_bytes(image[0x913a-0x8000:0x913c-0x8000],'little')
    # C.BNEZ, rs1'=a2. Decode the signed CB immediate rather than accepting
    # a mere hardcoded destination after checking the whole instruction.
    if h&3!=1 or (h>>13)&7!=7 or ((h>>7)&7)!=4: raise ValueError('not c.bnez a2')
    imm=(((h>>12)&1)<<8)|(((h>>10)&3)<<3)|(((h>>5)&3)<<6)|(((h>>3)&3)<<1)|(((h>>2)&1)<<5)
    if imm&0x100: imm-=0x200
    if 0x913a+imm!=0x9188: raise ValueError('wrong branch target')
    if not 0<=delay<=0xffffffff: raise ValueError('bad delay')
    return 0x9188 if delay else 0x913c


def main():
    image=z.v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=z.v.SHA: raise ValueError('firmware identity mismatch')
    if branch(image,0)!=0x913c or any(branch(image,x)!=0x9188 for x in (1,300,0xffffffff)): raise ValueError('branch mismatch')
    count=0
    for bits in range(1,0x7fff):
        words=[0xabcdef01 if bits&(1<<i) else 0 for i in range(15)]
        existing=next(i for i,x in enumerate(words) if x); free=next(i for i,x in enumerate(words) if not x)
        words[existing]=0x1333c
        if z.scan(image,words)[:2]!=(0x914a,free) or m.scan(image,words,0x1333c)[:2]!=(0x91a2,existing): raise ValueError('precedence mismatch')
        # Synthetic boundary: independent stack and argument values, no memory
        # effects or interleaving between the independent projections.
        _,_,_,_,_,zevents=ins.run(image,free,0x1333c,0x12345678,7,0x4000,0x1000,[0]*6)
        _,_,mevents=upd.run(image,existing,0,0x100,0x12345678,7,0x4000)
        if zevents[5]!=('write',z.BASE+12*free+4,4,0x1333c) or mevents[-2]!=('write',z.BASE+12*existing,1,0): raise ValueError('update projection mismatch')
        count+=1
    # Full zero-delay table falls into general callback scan, not direct failure.
    words=[0xabcdef01]*15; words[14]=0x1333c
    if z.scan(image,words)[0]!=0x9188 or m.scan(image,words,0x1333c)[:2]!=(0x91a2,14): raise ValueError('full fallback mismatch')
    # Corrupt condition/register and target separately.
    for offset,mask in ((0,0x80),(1,0x20),(0,0x04)):
        bad=bytearray(image); bad[0x913a-0x8000+offset]^=mask
        try: branch(bad,1)
        except ValueError: continue
        raise ValueError('branch mutant accepted')
    print(f'PASS: {count} mixed occupancy tables choose free slot for zero delay, existing match for nonzero delay')
    print('PASS: full zero-delay scan reaches fallback; assumed setup then finds existing callback; 3 branch mutations rejected')
    print('Independent synthetic projections, stable memory and normal reads assumed; no provider or hardware execution.')

if __name__=='__main__': main()
