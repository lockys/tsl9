"""Fixed original caller path 0xb2aa..0xb2f4; calls already returned zero.

Clock provider at 0x81b0 is a returning stub assumed not to mutate the stack,
gp or table. Reads succeed; memory aliases, interrupts and hardware omitted.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v',HERE/'verify.py'); v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
MASK=0xffffffff
OPS={0xb2aa:'b707050a',0xb2ae:'93870710',0xb2b2:'3ece',0xb2b4:'93874105',0xb2b8:'9c43',0xb2ba:'1810',0xb2bc:'83c70706',0xb2c0:'9983',0xb2c2:'ba97',0xb2c4:'03c6c7ff',0xb2c8:'bd67',0xb2ca:'938707a6',0xb2ce:'3306f602',0xb2d2:'32c6',0xb2d4:'efc0dfed',0xb2d8:'3246',0xb2da:'b250',0xb2dc:'8146',0xb2de:'3295',0xb2e0:'97170020',0xb2e4:'23a8a7c0',0xb2e8:'8145',0xb2ea:'17050000',0xb2ee:'1305a5f6',0xb2f2:'4561',0xb2f4:'6fd01fe3'}


def run(image,byte,clock,gp,pointer,sp,ra):
    if not 0<=byte<=255 or any(not 0<=x<=MASK for x in (clock,gp,pointer,sp,ra)): raise ValueError('bad input')
    pc=0xb2aa; a0=a1=a2=a3=a4=a5=0; events=[]; saved_delay=0; lookup=[]
    for _ in range(30):
        if pc==0x9124: return (a0,a1,a2,a3),sp,ra,tuple(events)
        op=bytes.fromhex(OPS[pc]); off=pc-0x8000
        if image[off:off+len(op)]!=op: raise ValueError(f'opcode mismatch {pc:#x}')
        if pc==0xb2aa: a5=0x0a050000; pc+=4
        elif pc==0xb2ae: a5=(a5+256)&MASK; pc+=4
        elif pc==0xb2b2: lookup=list(a5.to_bytes(4,'little')); events.append(('write',(sp+28)&MASK,4,a5)); pc+=2
        elif pc==0xb2b4: a5=(gp+84)&MASK; pc+=4
        elif pc==0xb2b8: events.append(('read',a5,4,pointer)); a5=pointer; pc+=2
        elif pc==0xb2ba: a4=(sp+32)&MASK; pc+=2
        elif pc==0xb2bc: events.append(('read',(a5+96)&MASK,1,byte)); a5=byte; pc+=4
        elif pc==0xb2c0: a5>>=6; pc+=2
        elif pc==0xb2c2: a5=(a5+a4)&MASK; pc+=2
        elif pc==0xb2c4:
            idx=(a5-4-((sp+28)&MASK))&MASK
            if idx>=4: raise ValueError('invalid lookup')
            a2=lookup[idx]; events.append(('read',(a5-4)&MASK,1,a2)); pc+=4
        elif pc==0xb2c8: a5=0xf000; pc+=2
        elif pc==0xb2ca: a5=(a5-1440)&MASK; pc+=4
        elif pc==0xb2ce: a2=(a2*a5)&MASK; pc+=4
        elif pc==0xb2d2: saved_delay=a2; events.append(('write',(sp+12)&MASK,4,a2)); pc+=2
        elif pc==0xb2d4: events.append(('call',0x81b0)); a0=clock; pc+=4
        elif pc==0xb2d8: a2=saved_delay; events.append(('read',(sp+12)&MASK,4,a2)); pc+=2
        elif pc==0xb2da: events.append(('read',(sp+44)&MASK,4,ra)); pc+=2
        elif pc==0xb2dc: a3=0; pc+=2
        elif pc==0xb2de: a0=(a0+a2)&MASK; pc+=2
        elif pc==0xb2e0: a5=(pc+0x20001000)&MASK; pc+=4
        elif pc==0xb2e4: events.append(('write',(a5-1008)&MASK,4,a0)); pc+=4
        elif pc==0xb2e8: a1=0; pc+=2
        elif pc==0xb2ea: a0=pc; pc+=4
        elif pc==0xb2ee: a0=(a0-150)&MASK; pc+=4
        elif pc==0xb2f2: sp=(sp+48)&MASK; pc+=2
        elif pc==0xb2f4: pc=0x9124
    raise ValueError('instruction limit')


def main():
    image=v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=v.SHA: raise ValueError('firmware identity mismatch')
    count=0
    for byte in range(256):
        for clock in (0,1,0xfffffff0,0xffffffff):
            for sp in (0x20001000,0xfffffff0):
                pointer=0x20001234; gp=0x20000000; ra=0x12345678
                delay=(0,60000,300000,600000)[byte>>6]
                args,end,ret,events=run(image,byte,clock,gp,pointer,sp,ra)
                expected=(('write',(sp+28)&MASK,4,0x0a050100),('read',gp+84,4,pointer),('read',pointer+96,1,byte),('read',(sp+28+(byte>>6))&MASK,1,(0,1,5,10)[byte>>6]),('write',(sp+12)&MASK,4,delay),('call',0x81b0),('read',(sp+12)&MASK,4,delay),('read',(sp+44)&MASK,4,ra),('write',0x2000bef0,4,(clock+delay)&MASK))
                if (args,end,ret,events)!=((0xb254,0,delay,0),(sp+48)&MASK,ra,expected): raise ValueError(f'caller mismatch byte {byte}')
                count+=1
    for addr in OPS:
        bad=bytearray(image); bad[addr-0x8000]^=1
        try: run(bad,0xff,0,0x20000000,0x20001234,0x20001000,1)
        except ValueError as e:
            if str(e).startswith('opcode mismatch'): continue
        raise ValueError(f'mutant accepted {addr:#x}')
    print(f'PASS: {count} bounded caller traces, all 256 data bytes; {len(OPS)} opcode mutations rejected')
    print('Inputs to 0x9124: callback=0xb254, mode=0, argument=0, delay in {0,60000,300000,600000}.')
    print('Conditional on two earlier zero returns; provider and hardware effects not executed.')

if __name__=='__main__': main()
