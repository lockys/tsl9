"""Compose 0xb254 callback with two 0x90b0 table projections.

Discrete segments, not continuous CPU execution. The first 0x90b0 returns;
indirect providers preserve the table except for modeled 0x90b0 writes, saved
stack word and gp. No aliases, races, faults, reachability or hardware claims.
"""
import hashlib
import importlib.util
import random
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
callback=load('callback',HERE/'data_delay_callback.py')
table=load('table',HERE.parent/'v4160-dispatch-148b4-model'/'callback_table_composition.py')


def run_case(image,byte,clock_word,keys,payloads,gp_byte):
    result=callback.run(image,byte,clock_word,0x20000000,0x20001234,0x20003000,0x12345678)
    kind,pc,a0,sp,ra,events=result
    if not (byte&192 and clock_word):
        if kind!='return' or any(e[0]=='call' for e in events): raise ValueError('unexpected call')
        return ('return',tuple(keys),tuple(payloads))
    if (kind,pc,a0,sp,ra)!=('tail',0x90b0,0xb29a,0x20003000,0x12345678): raise ValueError('callback boundary')
    if ('write',0x2000bef0,4,0) not in events or ('call',0x90b0,0xb254) not in events: raise ValueError('callback events')
    keys=list(keys); payloads=list(payloads); observed=[]
    for key in (0xb254,0xb29a):
        before_keys=keys[:]; before_payloads=payloads[:]
        typ,reads,calls,writes,regs=table.composed(image,key,keys,payloads,gp_byte)
        found=next((i for i,k in enumerate(before_keys) if k==key),None)
        if reads!=[table.scan.BASE+12*i+4 for i in range(15 if found is None else found+1)]: raise ValueError('scan order mismatch')
        if found is None:
            if (typ,calls,writes,regs)!=('miss',[],[],None): raise ValueError('miss effects')
        else:
            addr=table.scan.BASE+12*found
            expected_calls=[] if before_payloads[found]==0 else [(0x13572468,before_payloads[found])]
            if typ!='match' or calls!=expected_calls or writes!=[(addr+4,0),(addr+8,0)]: raise ValueError('match effects')
            if regs!=(gp_byte,1<<found,0x14800,0x20002000,0x22222222,0x33333333): raise ValueError('tail provider projection')
            keys[found]=0; payloads[found]=0
        observed.append((key,found))
    return (tuple(observed),tuple(keys),tuple(payloads))


def main():
    image=callback.v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=callback.v.SHA: raise ValueError('firmware identity mismatch')
    count=0
    for i in range(16):
        for j in range(16):
            if i==j and i<15: continue
            keys=[0]*15; payloads=[0]*15
            if i<15: keys[i]=0xb254; payloads[i]=0x1234
            if j<15: keys[j]=0xb29a; payloads[j]=0x5678
            observed,after,pafter=run_case(image,0xc0,1,keys,payloads,0xff)
            if observed!=((0xb254,None if i==15 else i),(0xb29a,None if j==15 else j)): raise ValueError('selected index mismatch')
            if any(after) or any(pafter): raise ValueError('selected entries not cleared')
            count+=1
    rng=random.Random(4160255)
    for n in range(5000):
        keys=[rng.choice((0,0xb254,0xb29a,0x7777)) for _ in range(15)]
        payloads=[rng.choice((0,rng.getrandbits(32))) for _ in range(15)]
        byte=rng.randrange(256); clock_word=rng.choice((0,rng.getrandbits(32)|1))
        run_case(image,byte,clock_word,keys,payloads,rng.randrange(256)); count+=1
    for addr in (0xb262,0x90c8,0x90fe):
        bad=bytearray(image); bad[addr-0x8000]^=4
        try: run_case(bad,0xc0,1,[0xb254,0xb29a]+[0]*13,[1]*15,9)
        except ValueError: pass
        else: raise ValueError(f'mutation missed {addr:#x}')
    print(f'PASS: {count} composed callback/table cases, two sequential keys and duplicate priority')
    print('PASS: callback and table opcode mutations rejected; provider side effects excluded')
    print('Separate projections and reconstructed state only; not continuous execution or hardware.')

if __name__=='__main__': main()
