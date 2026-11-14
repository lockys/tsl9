"""Bounded fixed-instruction interpreter for 0x135e6 with returning call stub."""
import hashlib
from pathlib import Path
BIN=Path(__file__).resolve().parents[2]/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
MASK=0xffffffff
OPS={0x135e6:'4167',0x135e8:'9796ff1f',0x135ec:'83d6e61a',0x135f0:'7917',0x135f2:'9797ff1f',0x135f6:'9387271a',0x135fa:'638ce600',0x135fe:'03c75700',0x13602:'1377f70f',0x13606:'11c7',0x13608:'03c74700',0x1360c:'1377f70f',0x13610:'15e3',0x13612:'83d66700',0x13616:'4167',0x13618:'7917',0x1361a:'0145',0x1361c:'6301d704',0x13620:'03c79700',0x13624:'1377f70f',0x13628:'1dcb',0x1362a:'03c58700',0x1362e:'1375f50f',0x13632:'15c5',0x13634:'4111',0x13636:'8547',0x13638:'8146',0x1363a:'1306c012',0x1363e:'8145',0x13640:'17050000',0x13644:'1305c5cf',0x13648:'06c6',0x1364a:'1797ff1f',0x1364e:'2305f714',0x13652:'ef503fad',0x13656:'b240',0x13658:'0545',0x1365a:'4101',0x1365c:'8280',0x1365e:'8280'}


def run(image, values, original_sp, original_ra, callee_return):
    if len(values)!=6 or any(not 0<=x<=0xffff for x in (values[0],values[3])) or any(not 0<=values[i]<=255 for i in (1,2,4,5)): raise ValueError('invalid input')
    mem=dict(zip((0x2000c796,0x2000c799,0x2000c798,0x2000c79a,0x2000c79d,0x2000c79c),values))
    pc,sp,ra=0x135e6,original_sp,original_ra
    a0=a1=a2=a3=a4=a5=0
    saved={}; events=[]
    for _ in range(45):
        op=bytes.fromhex(OPS[pc]); off=pc-0x8000
        if image[off:off+len(op)]!=op: raise ValueError(f'opcode mismatch {pc:#x}')
        if pc==0x135e6: a4=0x10000; pc+=2
        elif pc==0x135e8: a3=(pc+0x1fff9000)&MASK; pc+=4
        elif pc==0x135ec: addr=(a3+430)&MASK; events.append(('read',addr,2)); a3=mem[addr]; pc+=4
        elif pc==0x135f0: a4-=2; pc+=2
        elif pc==0x135f2: a5=(pc+0x1fff9000)&MASK; pc+=4
        elif pc==0x135f6: a5=(a5+418)&MASK; pc+=4
        elif pc==0x135fa: pc=0x13612 if a3==a4 else 0x135fe
        elif pc==0x135fe: addr=a5+5; events.append(('read',addr,1)); a4=mem[addr]; pc+=4
        elif pc==0x13602: a4&=255; pc+=4
        elif pc==0x13606: pc=0x13612 if a4==0 else 0x13608
        elif pc==0x13608: addr=a5+4; events.append(('read',addr,1)); a4=mem[addr]; pc+=4
        elif pc==0x1360c: a4&=255; pc+=4
        elif pc==0x13610: pc=0x13634 if a4 else 0x13612
        elif pc==0x13612: addr=a5+6; events.append(('read',addr,2)); a3=mem[addr]; pc+=4
        elif pc==0x13616: a4=0x10000; pc+=2
        elif pc==0x13618: a4-=2; pc+=2
        elif pc==0x1361a: a0=0; pc+=2
        elif pc==0x1361c: pc=0x1365e if a4==a3 else 0x13620
        elif pc==0x13620: addr=a5+9; events.append(('read',addr,1)); a4=mem[addr]; pc+=4
        elif pc==0x13624: a4&=255; pc+=4
        elif pc==0x13628: pc=0x1365e if a4==0 else 0x1362a
        elif pc==0x1362a: addr=a5+8; events.append(('read',addr,1)); a0=mem[addr]; pc+=4
        elif pc==0x1362e: a0&=255; pc+=4
        elif pc==0x13632: pc=0x1365e if a0==0 else 0x13634
        elif pc==0x13634: sp=(sp-16)&MASK; pc+=2
        elif pc==0x13636: a5=1; pc+=2
        elif pc==0x13638: a3=0; pc+=2
        elif pc==0x1363a: a2=300; pc+=4
        elif pc==0x1363e: a1=0; pc+=2
        elif pc==0x13640: a0=pc; pc+=4
        elif pc==0x13644: a0=(a0-772)&MASK; pc+=4
        elif pc==0x13648: saved[(sp+12)&MASK]=ra; pc+=2
        elif pc==0x1364a: a4=(pc+0x1fff9000)&MASK; pc+=4
        elif pc==0x1364e: events.append(('write',(a4+330)&MASK,1,a5)); pc+=4
        elif pc==0x13652: events.append(('call',0x9124,a0,a1,a2,a3)); ra=pc+4; a0=callee_return; pc+=4
        elif pc==0x13656: ra=saved[(sp+12)&MASK]; pc+=2
        elif pc==0x13658: a0=1; pc+=2
        elif pc==0x1365a: sp=(sp+16)&MASK; pc+=2
        elif pc in (0x1365c,0x1365e): return a0,sp,ra,tuple(events)
    raise ValueError('instruction limit')


def expected(v,sp,ra):
    h0,m0,a0,h1,m1,a1=v
    events=[('read',0x2000c796,2)]
    ok=False
    if h0!=0xfffe:
        events.append(('read',0x2000c799,1))
        if m0:
            events.append(('read',0x2000c798,1)); ok=bool(a0)
    if not ok:
        events.append(('read',0x2000c79a,2))
        if h1!=0xfffe:
            events.append(('read',0x2000c79d,1))
            if m1:
                events.append(('read',0x2000c79c,1)); ok=bool(a1)
    if ok: events.extend((('write',0x2000c794,1,1),('call',0x9124,0x1333c,0,300,0)))
    return int(ok),sp,ra,tuple(events)


def main():
    image=BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=SHA: raise ValueError('firmware identity mismatch')
    import itertools
    tests=list(itertools.product((0xfffe,0x1234),(0,1,2,255),(0,1,2,255),(0xfffe,0x1234),(0,1,2,255),(0,1,2,255)))
    cases=0
    for values in tests:
        for ret in (0,0xffffffff):
            actual=run(image,values,0x20001000,0x12345678,ret)
            if actual!=expected(values,0x20001000,0x12345678): raise ValueError(f'case mismatch {values}')
            cases+=1
    for address in OPS:
        changed=bytearray(image); changed[address-0x8000]^=1
        for values in tests:
            try: run(changed,values,0x20001000,0x12345678,0)
            except ValueError as e:
                if str(e).startswith('opcode mismatch'): break
        else: raise ValueError(f'mutant not reached {address:#x}')
    print(f'PASS: {cases} cases; short-circuit reads, write-before-call, return and {len(OPS)} opcode mutations')
    print('External 0x9124 is a normal-return stub; no hardware, concurrency or registration guarantee.')

if __name__=='__main__': main()
