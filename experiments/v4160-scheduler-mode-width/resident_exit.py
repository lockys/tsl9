"""Project 0x91e4 to resident tail transfer or normal return.

The ordinary resident is a synthetic returning stub. Reads are successful,
independent synthetic values; memory alias, traps and provider side effects are
not modeled. Caller-saved registers other than a0 are intentionally omitted.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v',HERE/'verify.py'); v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
MASK=0xffffffff
OPS={0x91e4:'b7070400',0x91e8:'31c0',0x91ea:'6244',0x91ec:'f240',0x91ee:'d244',0x91f0:'4249',0x91f2:'b249',0x91f4:'224a',0x91f6:'03a3c722',0x91fa:'0561',0x91fc:'0283',0x922c:'bc4f',0x922e:'8297',0x9230:'13351500',0x9234:'f240',0x9236:'6244',0x9238:'d244',0x923a:'4249',0x923c:'b249',0x923e:'224a',0x9240:'0561',0x9242:'8280'}


def run(image,mode,task,sp,saved,target,result):
    # saved: s0,ra,s1,s2,s3,s4 in stack positions 24,28,20,16,12,8.
    if len(saved)!=6 or any(not 0<=x<=MASK for x in (mode,task,sp,target,result,*saved)): raise ValueError('bad input')
    pc=0x91e4; a0=task; a5=0; t1=0; regs={}; events=[]
    mapping={0x91ea:('s0',0,24),0x91ec:('ra',1,28),0x91ee:('s1',2,20),0x91f0:('s2',3,16),0x91f2:('s3',4,12),0x91f4:('s4',5,8),0x9234:('ra',1,28),0x9236:('s0',0,24),0x9238:('s1',2,20),0x923a:('s2',3,16),0x923c:('s3',4,12),0x923e:('s4',5,8)}
    for _ in range(20):
        op=bytes.fromhex(OPS[pc]); off=pc-0x8000
        if image[off:off+len(op)]!=op: raise ValueError(f'opcode mismatch {pc:#x}')
        if pc==0x91e4: a5=0x40000; pc+=4
        elif pc==0x91e8: pc=0x922c if mode==0 else 0x91ea
        elif pc in mapping:
            name,i,offset=mapping[pc]; regs[name]=saved[i]; events.append(('read',(sp+offset)&MASK,4,saved[i])); pc+=2
        elif pc==0x91f6: events.append(('read',a5+556,4,target)); t1=target; pc+=4
        elif pc==0x91fa: sp=(sp+32)&MASK; pc+=2
        elif pc==0x91fc: return ('tail',t1,a0,sp,regs,tuple(events))
        elif pc==0x922c: events.append(('read',a5+88,4,target)); a5=target; pc+=2
        elif pc==0x922e: events.append(('call',a5,a0,0x9230)); a0=result; pc+=2
        elif pc==0x9230: a0=int(a0==0); pc+=4
        elif pc==0x9240: sp=(sp+32)&MASK; pc+=2
        elif pc==0x9242: return ('return',regs['ra'],a0,sp,regs,tuple(events))
    raise ValueError('instruction limit')


def main():
    image=v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=v.SHA: raise ValueError('firmware identity mismatch')
    saved=[0x10,0x20,0x30,0x40,0x50,0x60]; target=0x12345678
    for x in range(65536):
        for mode in (0,(x|0x10000)):
            result=x; sp=0xfffffff0 if x&1 else 0x1000; task=x
            kind,dest,a0,end,regs,events=run(image,mode,task,sp,saved,target,result)
            if regs!=dict(zip(('s0','ra','s1','s2','s3','s4'),saved)) or end!=(sp+32)&MASK: raise ValueError('restore mismatch')
            if mode==0:
                reads=tuple(('read',(sp+off)&MASK,4,saved[i]) for i,off in ((1,28),(0,24),(2,20),(3,16),(4,12),(5,8)))
                if (kind,dest,a0)!=('return',saved[1],int(result==0)) or events!=(('read',0x40058,4,target),('call',target,task,0x9230),*reads): raise ValueError('call exit mismatch')
            else:
                reads=tuple(('read',(sp+off)&MASK,4,saved[i]) for i,off in ((0,24),(1,28),(2,20),(3,16),(4,12),(5,8)))
                if (kind,dest,a0)!=('tail',target,task) or events!=(*reads,('read',0x4022c,4,target)): raise ValueError('tail exit mismatch')
    for addr in OPS:
        changed=bytearray(image); changed[addr-0x8000]^=1
        caught=False
        for mode in (0,1):
            try: run(changed,mode,0,0x1000,saved,target,0)
            except ValueError as e:
                if str(e).startswith('opcode mismatch'): caught=True; break
        if not caught: raise ValueError(f'opcode mutation not rejected {addr:#x}')
    print(f'PASS: 131072 resident-exit traces; {len(OPS)} opcode mutations rejected')
    print('mode=0 calls [0x40058] and returns (result==0); nonzero tail-jumps [0x4022c].')
    print('Provider return, pointer and stack values synthetic; provider side effects and hardware unknown.')

if __name__=='__main__': main()
