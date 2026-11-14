"""Nonzero-delay matching scan, bounded before match body or free scan.

Fixed original instructions only, successful stable reads; provider, previous
entry setup, full control flow, interrupts and real hardware are not modeled.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
v=load('v',HERE/'verify.py'); free=load('free',HERE/'free_scan.py')
BASE=0x2000be08
OPS={0x9196:'3e87',0x9198:'8144',0x919a:'bd46',0x919c:'5043',0x919e:'6310a606',0x91fe:'8504',0x9200:'3107',0x9202:'e39dd4f8'}


def scan(image,words,callback):
    if len(words)!=15 or not 0<=callback<=0xffffffff or any(not 0<=w<=0xffffffff for w in words): raise ValueError('bad inputs')
    pc=0x9196; a5=BASE; a4=s1=a3=a2=0; reads=[]
    for _ in range(100):
        if pc in (0x91a2,0x9206): return pc,s1,a5,tuple(reads)
        op=bytes.fromhex(OPS[pc]); off=pc-0x8000
        if image[off:off+len(op)]!=op: raise ValueError(f'opcode mismatch {pc:#x}')
        if pc==0x9196: a4=a5; pc+=2
        elif pc==0x9198: s1=0; pc+=2
        elif pc==0x919a: a3=15; pc+=2
        elif pc==0x919c:
            idx=(a4-BASE)//12
            if not 0<=idx<15 or a4!=BASE+idx*12: raise ValueError('bad read')
            reads.append(a4+4); a2=words[idx]; pc+=2
        elif pc==0x919e: pc=0x91fe if a2!=callback else 0x91a2
        elif pc==0x91fe: s1=(s1+1)&0xffffffff; pc+=2
        elif pc==0x9200: a4=(a4+12)&0xffffffff; pc+=2
        elif pc==0x9202: pc=0x919c if s1!=a3 else 0x9206
    raise ValueError('instruction limit')


def main():
    image=v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=v.SHA: raise ValueError('firmware identity mismatch')
    for callback in (0,0x1333c,0xffffffff):
        for bits in range(1<<15):
            other=1 if callback==0 else 0
            words=[callback if bits&(1<<i) else other for i in range(15)]
            index=next((i for i,x in enumerate(words) if x==callback),15)
            expected=(0x91a2 if index<15 else 0x9206,index,BASE,tuple(BASE+12*i+4 for i in range(min(index+1,15))))
            if scan(image,words,callback)!=expected: raise ValueError(f'match mismatch {callback:#x}/{bits:#x}')
            if index==15:
                dest,free_index,_,_,_=free.scan(image,words)
                expected_free=0 if callback!=0 else 15
                if free_index!=expected_free or dest!=(0x920e if expected_free==0 else 0x9234): raise ValueError('composed zero-key mismatch')
    # All 3-state tables across the first nine slots, remaining slots occupied:
    # zero, matching callback, and different occupied callback. This exercises
    # duplicate matches and cases where a free slot precedes a later match.
    callback=0x1333c
    for encoded in range(3**9):
        value=encoded; words=[]
        for _ in range(9):
            words.append((0,callback,0xabcdef01)[value%3]); value//=3
        words.extend([0xabcdef01]*6)
        match=next((i for i,x in enumerate(words) if x==callback),15)
        pc,idx,_,_=scan(image,words,callback)
        if idx!=match or pc!=(0x91a2 if match<15 else 0x9206): raise ValueError('ternary match mismatch')
        if match==15:
            empty=next((i for i,x in enumerate(words) if x==0),15)
            dest,actual,_,_,_=free.scan(image,words)
            if actual!=empty or dest!=(0x920e if empty<15 else 0x9234): raise ValueError('ternary free mismatch')
    # All eight opcodes executed on a nonmatching table. Matching branch is
    # tested above for each position, but no match-body instructions are run.
    for addr in OPS:
        bad=bytearray(image); bad[addr-0x8000]^=1
        try: scan(bad,[0]*15,0x1333c)
        except ValueError as e:
            if str(e).startswith('opcode mismatch'): continue
        raise ValueError(f'unrejected opcode mutant {addr:#x}')
    print('PASS: 98304 synthetic matching bitmaps; first equal word or 15-word miss')
    print('PASS: 19683 mixed ternary tables; matching precedes free-slot search')
    print('PASS: composed misses show callback zero requires full nonzero table under stable reads')
    print('PASS: 8 instruction mutations rejected; no provider or hardware execution')

if __name__=='__main__': main()
