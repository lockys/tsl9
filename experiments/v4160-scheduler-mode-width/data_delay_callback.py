"""Fixed-instruction projection of callback 0xb254 to return or 0x90b0 tail.

0x90b0 is a returning stub preserving the saved stack word. Memory reads are
synthetic, independent and successful; no alias, traps, interrupts or hardware.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v',HERE/'verify.py'); v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
MASK=0xffffffff
OPS={0xb254:'93874105',0xb258:'9c43',0xb25a:'83c70706',0xb25e:'93f7070c',0xb262:'9dcb',0xb264:'97170020',0xb268:'938787c8',0xb26c:'dc43',0xb26e:'8dc7',0xb270:'4111',0xb272:'17050000',0xb276:'130525fe',0xb27a:'06c6',0xb27c:'97170020',0xb280:'23aa07c6',0xb284:'efd0dfe2',0xb288:'b240',0xb28a:'17050000',0xb28e:'13050501',0xb292:'4101',0xb294:'6fd0dfe1',0xb298:'8280'}


def run(image,byte,word,gp,pointer,sp,ra):
    if not 0<=byte<=255 or any(not 0<=x<=MASK for x in (word,gp,pointer,sp,ra)): raise ValueError('bad input')
    pc=0xb254; a0=a5=0; events=[]; original_ra=ra
    for _ in range(30):
        if pc==0x90b0: return ('tail',pc,a0,sp,ra,tuple(events))
        op=bytes.fromhex(OPS[pc]); off=pc-0x8000
        if image[off:off+len(op)]!=op: raise ValueError(f'opcode mismatch {pc:#x}')
        if pc==0xb254: a5=(gp+84)&MASK; pc+=4
        elif pc==0xb258: events.append(('read',a5,4,pointer)); a5=pointer; pc+=2
        elif pc==0xb25a: events.append(('read',(a5+96)&MASK,1,byte)); a5=byte; pc+=4
        elif pc==0xb25e: a5&=192; pc+=4
        elif pc==0xb262: pc=0xb298 if not a5 else 0xb264
        elif pc==0xb264: a5=(pc+0x20001000)&MASK; pc+=4
        elif pc==0xb268: a5=(a5-888)&MASK; pc+=4
        elif pc==0xb26c: events.append(('read',(a5+4)&MASK,4,word)); a5=word; pc+=2
        elif pc==0xb26e: pc=0xb298 if not a5 else 0xb270
        elif pc==0xb270: sp=(sp-16)&MASK; pc+=2
        elif pc==0xb272: a0=pc; pc+=4
        elif pc==0xb276: a0=(a0-30)&MASK; pc+=4
        elif pc==0xb27a: events.append(('write',(sp+12)&MASK,4,ra)); pc+=2
        elif pc==0xb27c: a5=(pc+0x20001000)&MASK; pc+=4
        elif pc==0xb280: events.append(('write',(a5-908)&MASK,4,0)); pc+=4
        elif pc==0xb284: events.append(('call',0x90b0,a0)); ra=pc+4; a0=0xdeadbeef; pc+=4
        elif pc==0xb288: events.append(('read',(sp+12)&MASK,4,original_ra)); ra=original_ra; pc+=2
        elif pc==0xb28a: a0=pc; pc+=4
        elif pc==0xb28e: a0=(a0+16)&MASK; pc+=4
        elif pc==0xb292: sp=(sp+16)&MASK; pc+=2
        elif pc==0xb294: pc=0x90b0
        elif pc==0xb298: return ('return',ra,None,sp,ra,tuple(events))
    raise ValueError('instruction limit')


def main():
    image=v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=v.SHA: raise ValueError('firmware identity mismatch')
    count=0
    for byte in range(256):
        for word in (0,1,0xffffffff):
            for sp in (0x20001000,0xfffffff0):
                gp=0x20000000; ptr=0x20001234; ra=0x12345678
                actual=run(image,byte,word,gp,ptr,sp,ra)
                events=[('read',gp+84,4,ptr),('read',ptr+96,1,byte)]
                if byte&192: events.append(('read',0x2000bef0,4,word))
                if byte&192 and word:
                    events.extend([('write',(sp-4)&MASK,4,ra),('write',0x2000bef0,4,0),('call',0x90b0,0xb254),('read',(sp-4)&MASK,4,ra)])
                    expected=('tail',0x90b0,0xb29a,sp,ra,tuple(events))
                else: expected=('return',ra,None,sp,ra,tuple(events))
                if actual!=expected: raise ValueError(f'callback mismatch byte={byte}, word={word}')
                count+=1
    for pc in OPS:
        bad=bytearray(image); bad[pc-0x8000]^=1
        for byte,word in ((0,0),(0xc0,0),(0xc0,1)):
            try: run(bad,byte,word,0x20000000,0x20001234,0x20001000,0x12345678)
            except ValueError as e:
                if str(e).startswith('opcode mismatch'): break
        else: raise ValueError(f'mutant accepted {pc:#x}')
    print(f'PASS: {count} callback traces across all byte values; {len(OPS)} opcode mutations rejected')
    print('High bits zero or 0x2000bef0 zero => return; otherwise clear word, call 0x90b0(0xb254), tail 0x90b0(0xb29a).')
    print('0x90b0 is a returning stub; provider effects, reachability and hardware unknown.')

if __name__=='__main__': main()
