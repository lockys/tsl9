"""Fixed-instruction execution of 0x13d88 tail, with 0x81b0 stubbed."""
import hashlib
from pathlib import Path

BIN = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
MASK = 0xffffffff
OPS = {
    0x13d88:'09cd', 0x13d8a:'8146', 0x13d8c:'13064006', 0x13d90:'b240',
    0x13d92:'8145', 0x13d94:'17f5ffff', 0x13d98:'1305255b', 0x13d9c:'4101',
    0x13d9e:'6f506fb8', 0x13da2:'ef40efc0', 0x13da6:'93878115', 0x13daa:'9c43',
    0x13dac:'13072002', 0x13db0:'b307f540', 0x13db4:'6379f700', 0x13db8:'b240',
    0x13dba:'23aca114', 0x13dbe:'0145', 0x13dc0:'4101', 0x13dc2:'6ff04fd8',
    0x13dc6:'8146', 0x13dc8:'13063002', 0x13dcc:'d1b7',
}


def run(image, result, clock, previous, gp, original_sp, original_ra):
    pc = 0x13d88
    a0, a1, a2, a3, a4, a5 = result, None, None, None, None, None
    sp, ra = (original_sp-16)&MASK, 0x13d50
    saved = {(original_sp-4)&MASK: original_ra}
    reads, writes, calls = [], [], []
    for _ in range(25):
        if pc in (0x9124, 0x13346):
            args = (a0, a1, a2, a3) if pc == 0x9124 else (a0,)
            return pc, args, sp, ra, tuple(reads), tuple(writes), tuple(calls)
        expected = bytes.fromhex(OPS[pc]); off = pc-0x8000
        if image[off:off+len(expected)] != expected: raise ValueError(f'opcode mismatch {pc:#x}')
        if pc == 0x13d88: pc = 0x13da2 if a0 == 0 else 0x13d8a
        elif pc == 0x13d8a: a3=0; pc+=2
        elif pc == 0x13d8c: a2=100; pc+=4
        elif pc == 0x13d90: ra=saved[(sp+12)&MASK]; pc+=2
        elif pc == 0x13d92: a1=0; pc+=2
        elif pc == 0x13d94: a0=(pc+0xfffff000)&MASK; pc+=4
        elif pc == 0x13d98: a0=(a0+1458)&MASK; pc+=4
        elif pc == 0x13d9c: sp=(sp+16)&MASK; pc+=2
        elif pc == 0x13d9e: pc=0x9124
        elif pc == 0x13da2: calls.append(0x81b0); ra=pc+4; a0=clock; pc+=4
        elif pc == 0x13da6: a5=(gp+344)&MASK; pc+=4
        elif pc == 0x13daa: reads.append(a5); a5=previous; pc+=2
        elif pc == 0x13dac: a4=34; pc+=4
        elif pc == 0x13db0: a5=(a0-a5)&MASK; pc+=4
        elif pc == 0x13db4: pc=0x13dc6 if a4>=a5 else 0x13db8
        elif pc == 0x13db8: ra=saved[(sp+12)&MASK]; pc+=2
        elif pc == 0x13dba: writes.append(((gp+344)&MASK,a0)); pc+=4
        elif pc == 0x13dbe: a0=0; pc+=2
        elif pc == 0x13dc0: sp=(sp+16)&MASK; pc+=2
        elif pc == 0x13dc2: pc=0x13346
        elif pc == 0x13dc6: a3=0; pc+=2
        elif pc == 0x13dc8: a2=35; pc+=4
        elif pc == 0x13dcc: pc=0x13d90
    raise ValueError('instruction limit')


def main():
    image = BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=SHA: raise ValueError('firmware identity mismatch')
    count=0
    for previous in (0, 0x10, 0xffffffef, 0xffffffff):
        for delta in list(range(65536))+[0x7fffffff,0x80000000,0xffffffff]:
            clock=(previous+delta)&MASK
            for result in (0,1,0xffffffff):
                gp, sp, ra = 0xfffffff0, 0x20001000, 0x12345678
                actual=run(image,result,clock,previous,gp,sp,ra)
                addr=(gp+344)&MASK
                if result:
                    expected=(0x9124,(0x13346,0,100,0),sp,ra,(),(),())
                elif delta<=34:
                    expected=(0x9124,(0x13346,0,35,0),sp,ra,(addr,),(),(0x81b0,))
                else:
                    expected=(0x13346,(0,),sp,ra,(addr,),((addr,clock),),(0x81b0,))
                if actual!=expected: raise ValueError(f'tail mismatch p={previous:#x} d={delta:#x} r={result:#x}')
                count+=1
    tests=[(1,0,0),(0,34,0),(0,35,0)]
    for address in OPS:
        changed=bytearray(image); changed[address-0x8000]^=1
        for result,clock,previous in tests:
            try: run(changed,result,clock,previous,0x20000000,0x20001000,0x12345678)
            except ValueError as e:
                if str(e).startswith('opcode mismatch'): break
        else: raise ValueError(f'mutant not reached: {address:#x}')
    print(f'PASS: {count} traces; unsigned wrap and threshold 34/35; {len(OPS)} opcode mutations rejected')
    print('Fixed instruction table and returning 0x81b0 stub; no tail target or hardware execution.')


if __name__=='__main__': main()
