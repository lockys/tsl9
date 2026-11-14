"""Bounded matched-slot update, stops at common arithmetic 0x91d0.

A nonzero old argument triggers an indirect provider stub assumed to return
and preserve s0/s1/s2/s4/gp. It may otherwise have unknown side effects;
this projection only records the call and explicit instructions' accesses.
"""
import hashlib
import importlib.util
import random
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v',HERE/'verify.py'); v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
BASE=0x2000be08
OPS={0x91a2:'b147',0x91a4:'b387f402',0x91a8:'ca97',0x91aa:'8847',0x91ac:'09c5',0x91ae:'b7070400',0x91b2:'bc57',0x91b4:'8297',0x91b6:'b147',0x91b8:'b387f402',0x91bc:'8545',0x91be:'03c5610a',0x91c2:'b3959500',0x91c6:'ca97',0x91c8:'23808700',0x91cc:'23a44701'}


def run(image,index,old_argument,mode,new_argument,task,target):
    if not 0<=index<15 or not 0<=task<256 or any(not 0<=x<=0xffffffff for x in (old_argument,mode,new_argument,target)): raise ValueError('bad input')
    pc=0x91a2; a5=a0=a1=0; s1=index; s2=BASE; s0=mode; s4=new_argument; events=[]
    for _ in range(20):
        if pc==0x91d0: return a0,a1,tuple(events)
        op=bytes.fromhex(OPS[pc]); off=pc-0x8000
        if image[off:off+len(op)]!=op: raise ValueError(f'opcode mismatch {pc:#x}')
        if pc==0x91a2: a5=12; pc+=2
        elif pc==0x91a4: a5=(s1*a5)&0xffffffff; pc+=4
        elif pc==0x91a8: a5=(a5+s2)&0xffffffff; pc+=2
        elif pc==0x91aa: events.append(('read',a5+8,4,old_argument)); a0=old_argument; pc+=2
        elif pc==0x91ac: pc=0x91b6 if a0==0 else 0x91ae
        elif pc==0x91ae: a5=0x40000; pc+=4
        elif pc==0x91b2: events.append(('read',a5+104,4,target)); a5=target; pc+=2
        elif pc==0x91b4: events.append(('call',a5,a0)); a5=0xdeadbeef; a0=0x87654321; pc+=2
        elif pc==0x91b6: a5=12; pc+=2
        elif pc==0x91b8: a5=(s1*a5)&0xffffffff; pc+=4
        elif pc==0x91bc: a1=1; pc+=2
        elif pc==0x91be: events.append(('read','gp+166',1,task)); a0=task; pc+=4
        elif pc==0x91c2: a1=(a1<<(s1&31))&0xffffffff; pc+=4
        elif pc==0x91c6: a5=(a5+s2)&0xffffffff; pc+=2
        elif pc==0x91c8: events.append(('write',a5,1,s0&255)); pc+=4
        elif pc==0x91cc: events.append(('write',a5+8,4,s4)); pc+=4
    raise ValueError('instruction limit')


def main():
    image=v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=v.SHA: raise ValueError('firmware identity mismatch')
    count=0
    for index in range(15):
        slot=BASE+12*index
        for old in (0,1,0x12345678,0xffffffff):
            for mode in (0,1,255,256,0xffffffff):
                for new in (0,0x87654321,0xffffffff):
                    for task in (0,255):
                        target=0x12345678
                        events=[('read',slot+8,4,old)]
                        if old: events.extend([('read',0x40068,4,target),('call',target,old)])
                        events.extend([('read','gp+166',1,task),('write',slot,1,mode&255),('write',slot+8,4,new)])
                        if run(image,index,old,mode,new,task,target)!=(task,1<<index,tuple(events)): raise ValueError('projection mismatch')
                        count+=1
    spec2=importlib.util.spec_from_file_location('match_scan',HERE/'match_scan.py'); match=importlib.util.module_from_spec(spec2); spec2.loader.exec_module(match)
    rng=random.Random(4160)
    for _ in range(6000):
        callback=0x1333c; chosen=rng.randrange(15)
        words=[rng.choice((0,0xabcdef01)) for _ in range(15)]
        words[chosen]=callback
        if rng.randrange(2): words[rng.randrange(chosen,15)]=callback
        pc,index,_,_=match.scan(image,words,callback)
        if pc!=0x91a2 or index!=chosen: raise ValueError('match composition index')
        old=rng.choice((0,rng.getrandbits(32)|1)); mode=rng.getrandbits(32); new=rng.getrandbits(32); task=rng.randrange(256)
        a0,a1,events=run(image,index,old,mode,new,task,0x12345678)
        if (a0,a1)!=(task,1<<chosen) or events[-2:]!=(('write',BASE+12*chosen,1,mode&255),('write',BASE+12*chosen+8,4,new)): raise ValueError('match composition update')
    for address in OPS:
        changed=bytearray(image); changed[address-0x8000]^=1
        try: run(changed,0,1,256,0,0,0x12345678)
        except ValueError as e:
            if str(e).startswith('opcode mismatch'): continue
        raise ValueError(f'opcode mutant not rejected {address:#x}')
    print(f'PASS: {count} matched-slot traces, {len(OPS)} opcode mutants rejected')
    print('PASS: 6000 scan-to-update boundary compositions')
    print('Old argument nonzero calls [0x40068] before writes; callback word is not explicitly written.')
    print('Provider is a returning stub; side effects, valid targets and hardware are unknown.')

if __name__=='__main__': main()
