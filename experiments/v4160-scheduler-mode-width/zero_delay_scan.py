"""Zero-delay initial free-slot scan, limited to 0x913c–0x914a/0x9188.

Assumes the earlier branch selected zero delay, s2=0x2000be08 and all table
reads succeed. Stops before slot insertion or the general fallback setup.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v',HERE/'verify.py'); v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
BASE=0x2000be08
OPS={0x913c:'ca87',0x913e:'0147',0x9140:'3d48',0x9142:'83a84700',0x9146:'639d0802',0x9180:'0507',0x9182:'b107',0x9184:'e31f07fb'}


def scan(image,words):
    if len(words)!=15 or any(not 0<=x<=0xffffffff for x in words): raise ValueError('bad table')
    pc=0x913c; a5=a4=a6=a7=0; reads=[]
    for _ in range(100):
        if pc in (0x914a,0x9188): return pc,a4,a5,tuple(reads)
        op=bytes.fromhex(OPS[pc]); off=pc-0x8000
        if image[off:off+len(op)]!=op: raise ValueError(f'opcode mismatch {pc:#x}')
        if pc==0x913c: a5=BASE; pc+=2
        elif pc==0x913e: a4=0; pc+=2
        elif pc==0x9140: a6=15; pc+=2
        elif pc==0x9142:
            idx=(a5-BASE)//12
            if not 0<=idx<15 or a5!=BASE+12*idx: raise ValueError('read outside table')
            reads.append(a5+4); a7=words[idx]; pc+=4
        elif pc==0x9146: pc=0x9180 if a7!=0 else 0x914a
        elif pc==0x9180: a4=(a4+1)&0xffffffff; pc+=2
        elif pc==0x9182: a5=(a5+12)&0xffffffff; pc+=2
        elif pc==0x9184: pc=0x9142 if a4!=a6 else 0x9188
    raise ValueError('instruction limit')


def main():
    image=v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=v.SHA: raise ValueError('firmware identity mismatch')
    for bits in range(1<<15):
        words=[(0x80000000|i) if bits&(1<<i) else 0 for i in range(15)]
        first=next((i for i,x in enumerate(words) if x==0),15)
        expected=(0x914a if first<15 else 0x9188,first,BASE+12*first,tuple(BASE+12*i+4 for i in range(min(first+1,15))))
        if scan(image,words)!=expected: raise ValueError(f'bitmap mismatch {bits:#x}')
    for addr in OPS:
        bad=bytearray(image); bad[addr-0x8000]^=1
        try: scan(bad,[1]*15)
        except ValueError as e:
            if str(e).startswith('opcode mismatch'): continue
        raise ValueError(f'undetected mutation {addr:#x}')
    print('PASS: 32768 zero-delay occupancy bitmaps; ordered first-empty scan or full fallback')
    print('PASS: 8 opcode mutations rejected; no insertion, provider or hardware execution')

if __name__=='__main__': main()
