"""Fixed scheduler arithmetic 0x91d0–0x91e8, supporting zero delay too."""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v',HERE/'verify.py'); v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
MASK=0xffffffff
OPS={0x91d0:'9307803e',0x91d4:'3386f902',0x91d8:'c205',0x91da:'93071027',0x91de:'c181',0x91e0:'3356f602',0x91e4:'b7070400',0x91e8:'31c0'}


def run(image,mask,delay,mode):
    if any(not 0<=x<=MASK for x in (mask,delay,mode)): raise ValueError('bad input')
    pc=0x91d0; a1=mask; a2=a5=0
    for _ in range(9):
        if pc in (0x91ea,0x922c): return pc,a1,a2,a5
        op=bytes.fromhex(OPS[pc]); off=pc-0x8000
        if image[off:off+len(op)]!=op: raise ValueError(f'opcode mismatch {pc:#x}')
        if pc==0x91d0: a5=1000; pc+=4
        elif pc==0x91d4: a2=(delay*a5)&MASK; pc+=4
        elif pc==0x91d8: a1=(a1<<16)&MASK; pc+=2
        elif pc==0x91da: a5=625; pc+=4
        elif pc==0x91de: a1>>=16; pc+=2
        elif pc==0x91e0: a2//=a5; pc+=4
        elif pc==0x91e4: a5=0x40000; pc+=4
        elif pc==0x91e8: pc=0x922c if mode==0 else 0x91ea
    raise ValueError('instruction limit')


def main():
    image=v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=v.SHA: raise ValueError('firmware identity mismatch')
    for x in range(65536):
        for mode in (0,0x100):
            delay=((x*65537)^0x80000000)&MASK; mask=(x*65539)&MASK
            expected=(0x922c if mode==0 else 0x91ea,mask&65535,((delay*1000)&MASK)//625,0x40000)
            if run(image,mask,delay,mode)!=expected: raise ValueError('common mismatch')
    for pc in OPS:
        bad=bytearray(image); bad[pc-0x8000]^=1
        try: run(bad,1,0,0)
        except ValueError as e:
            if str(e).startswith('opcode mismatch'): continue
        raise ValueError(f'mutant accepted {pc:#x}')
    print('PASS: 131072 common arithmetic projections; 8 instruction mutations rejected')
    print('Delay multiply wraps at 32 bits before unsigned division; zero delay is supported.')

if __name__=='__main__': main()
