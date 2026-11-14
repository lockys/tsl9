"""Bounded original 0x9124 free-slot write and resident selector witness.

Starts at 0x920e after assumed nonzero-delay scan has selected a free slot;
stops before either resident path. It does not execute the scan or provider.
"""
import hashlib
from pathlib import Path
BIN=Path(__file__).resolve().parents[2]/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
MASK=0xffffffff
OPS={0x920e:'b147',0x9210:'b307f702',0x9214:'8545',0x9216:'b395e500',0x921a:'ca97',0x921c:'c8c3',0x921e:'23808700',0x9222:'23a44701',0x9226:'03c5610a',0x922a:'5db7',0x91d0:'9307803e',0x91d4:'3386f902',0x91d8:'c205',0x91da:'93071027',0x91de:'c181',0x91e0:'3356f602',0x91e4:'b7070400',0x91e8:'31c0'}


def run(image,index,callback,mode,delay,argument,task):
    if not 0<=index<15 or not 0<=task<256 or not all(0<=v<=MASK for v in (callback,mode,delay,argument)) or delay==0: raise ValueError('invalid bounded input')
    pc=0x920e; a0=callback; a4=index; s0=mode; s2=0x2000be08; s3=delay; s4=argument
    a1=a2=a5=0; events=[]
    for _ in range(20):
        if pc in (0x91ea,0x922c): return pc,a0,a1,a2,tuple(events)
        op=bytes.fromhex(OPS[pc]); off=pc-0x8000
        if image[off:off+len(op)]!=op: raise ValueError(f'opcode mismatch {pc:#x}')
        if pc==0x920e: a5=12; pc+=2
        elif pc==0x9210: a5=(a4*a5)&MASK; pc+=4
        elif pc==0x9214: a1=1; pc+=2
        elif pc==0x9216: a1=(a1<<(a4&31))&MASK; pc+=4
        elif pc==0x921a: a5=(a5+s2)&MASK; pc+=2
        elif pc==0x921c: events.append(('write',a5+4,4,a0)); pc+=2
        elif pc==0x921e: events.append(('write',a5,1,s0&255)); pc+=4
        elif pc==0x9222: events.append(('write',a5+8,4,s4)); pc+=4
        elif pc==0x9226: events.append(('read','gp+166',1)); a0=task; pc+=4
        elif pc==0x922a: pc=0x91d0
        elif pc==0x91d0: a5=1000; pc+=4
        elif pc==0x91d4: a2=(s3*a5)&MASK; pc+=4
        elif pc==0x91d8: a1=(a1<<16)&MASK; pc+=2
        elif pc==0x91da: a5=625; pc+=4
        elif pc==0x91de: a1>>=16; pc+=2
        elif pc==0x91e0: a2//=a5; pc+=4
        elif pc==0x91e4: a5=0x40000; pc+=4
        elif pc==0x91e8: pc=0x922c if s0==0 else 0x91ea
    raise ValueError('instruction limit')


def main():
    image=BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=SHA: raise ValueError('firmware identity mismatch')
    modes=(0,1,255,256,257,0x10000,0x80000000,0xffffffff)
    delays=(1,34,35,100,300,0x418937,0x418938,0xffffffff)
    count=0
    for index in range(15):
        for mode in modes:
            for delay in delays:
                for task in (0,255):
                    slot=0x2000be08+12*index
                    actual=run(image,index,0x1333c,mode,delay,0x87654321,task)
                    expected=(0x922c if mode==0 else 0x91ea,task,(1<<index)&0xffff,((delay*1000)&MASK)//625,
                              (('write',slot+4,4,0x1333c),('write',slot,1,mode&255),('write',slot+8,4,0x87654321),('read','gp+166',1)))
                    if actual!=expected: raise ValueError(f'mismatch index={index} mode={mode:#x} delay={delay:#x}')
                    count+=1
    zero=run(image,0,0x1333c,0,300,0,0)
    wide=run(image,0,0x1333c,256,300,0,0)
    if zero[4][1]!=wide[4][1] or (zero[0],wide[0],wide[2:4])!=(0x922c,0x91ea,(1,480)): raise ValueError('width witness mismatch')
    for address in OPS:
        changed=bytearray(image); changed[address-0x8000]^=1
        try: run(changed,0,0x1333c,0,300,0,0)
        except ValueError as e:
            if str(e).startswith('opcode mismatch'): continue
        raise ValueError(f'opcode mutant not rejected {address:#x}')
    print(f'PASS: {count} bounded traces; {len(OPS)} instruction mutations rejected')
    print('PASS: mode 0 and 0x100 store 0, but select 0x922c and 0x91ea respectively; index 0, delay 300 => mask 1, scaled 480')
    print('Free-slot selection assumed; resident transfer, effects and hardware not executed.')

if __name__=='__main__': main()
