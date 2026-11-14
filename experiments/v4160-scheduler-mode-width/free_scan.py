"""Fixed-instruction scan from 0x9206 after prior match scan has failed.

Assumes a5=0x2000be08 and successful stable word reads. Stops at selected
0x920e or at 0x9234 before epilogue; does not execute prior matching scan.
"""
import hashlib
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('v',Path(__file__).with_name('verify.py'))
v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
OPS={0x9206:'0147',0x9208:'bd46',0x920a:'d043',0x920c:'05ee',0x9244:'0507',0x9246:'b107',0x9248:'e311d7fc',0x924c:'0545',0x924e:'ddb7'}
BASE=0x2000be08


def scan(image,words):
    if len(words)!=15 or any(not 0<=w<=0xffffffff for w in words): raise ValueError('expected 15 unsigned words')
    pc=0x9206; a5=BASE; a4=a3=a2=a0=0; reads=[]
    for _ in range(100):
        if pc in (0x920e,0x9234): return pc,a4,a5,a0,tuple(reads)
        op=bytes.fromhex(OPS[pc]); off=pc-0x8000
        if image[off:off+len(op)]!=op: raise ValueError(f'opcode mismatch {pc:#x}')
        if pc==0x9206: a4=0; pc+=2
        elif pc==0x9208: a3=15; pc+=2
        elif pc==0x920a:
            address=a5+4; idx=(address-BASE-4)//12
            if address!=BASE+12*idx+4 or not 0<=idx<15: raise ValueError('out-of-range read')
            reads.append(address); a2=words[idx]; pc+=2
        elif pc==0x920c: pc=0x9244 if a2 else 0x920e
        elif pc==0x9244: a4=(a4+1)&0xffffffff; pc+=2
        elif pc==0x9246: a5=(a5+12)&0xffffffff; pc+=2
        elif pc==0x9248: pc=0x920a if a4!=a3 else 0x924c
        elif pc==0x924c: a0=1; pc+=2
        elif pc==0x924e: pc=0x9234
    raise ValueError('instruction limit')


def main():
    image=v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=v.SHA: raise ValueError('firmware identity mismatch')
    for bitmap in range(1<<15):
        words=[(0x80000000|i) if bitmap&(1<<i) else 0 for i in range(15)]
        index=next((i for i,w in enumerate(words) if w==0),15)
        result=scan(image,words)
        expected=(0x920e if index<15 else 0x9234,index,BASE+12*index,0 if index<15 else 1,tuple(BASE+12*i+4 for i in range(min(index+1,15))))
        if result!=expected: raise ValueError(f'scan mismatch bitmap {bitmap:#x}')
        if index<15:
            pc,task,mask,scaled,events=v.run(image,index,0x1333c,0,300,0,7)
            if (pc,task,mask,scaled)!=(0x922c,7,1<<index,480) or events[0]!=('write',BASE+12*index+4,4,0x1333c): raise ValueError('projection composition mismatch')
    for address in OPS:
        changed=bytearray(image); changed[address-0x8000]^=1
        try: scan(changed,[1]*15)
        except ValueError as e:
            if str(e).startswith('opcode mismatch'): continue
        raise ValueError(f'opcode mutation not rejected at {address:#x}')
    print('PASS: all 32768 occupancy bitmaps; first empty or full result, ordered reads')
    print('PASS: 32767 selected-slot compositions; 9 instruction mutations rejected')
    print('Prior matching scan, resident transfers, concurrency and hardware not executed.')

if __name__=='__main__': main()
