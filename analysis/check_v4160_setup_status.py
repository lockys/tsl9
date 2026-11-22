"""Track returned a0 through the APP caller. Callees are injected normal returns."""
from hashlib import sha256
from itertools import product
from pathlib import Path

APP = Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')

def need(ok):
    if not ok: raise ValueError('setup status mismatch')

def sx(v, n): return (v ^ (1 << (n-1))) - (1 << (n-1))

def follow(code, initial, outcomes):
    pc = 0x16e96  # just after the entry poll returned
    regs = {10:initial, 8:1}; calls = []
    for _ in range(80):
        w = int.from_bytes(code[pc-32768:pc-32768+4], 'little'); h = w & 65535
        if w & 3 != 3:
            if h == 0xed31: pc += 92 if regs[10] else 2; continue  # c.bnez a0,+92
            if h in (0x84aa,0x8522,0x8526,0x852a): regs[h>>7&31] = regs[h>>2&31]
            elif h >> 13 == 2 and h&3 == 1: regs[h>>7&31] = sx((h>>2&31)|(h>>12&1)<<5,6)
            elif pc in (0x16ef4,0x16ef6,0x16efa,0x16efc):
                need(h == {0x16ef4:0x40b2,0x16ef6:0x4422,0x16efa:0x4492,0x16efc:0x0141}[pc])
            elif pc == 0x16efe and h == 0x8082: return calls, regs[10]
            else: raise ValueError(hex(pc))
            pc += 2
        elif w & 127 == 0x6f and w>>7&31 == 1:
            off = ((w>>31)<<20 | (w>>12&255)<<12 | (w>>20&1)<<11 | (w>>21&1023)<<1)
            calls.append(pc + sx(off,21)); regs[10] = outcomes[len(calls)-1]; pc += 4
        elif w & 0xff07f == 0x13: regs[w>>7&31] = sx(w>>20,12); pc += 4
        else: raise ValueError(hex(pc))
    raise ValueError('budget')

if __name__ == '__main__':
    code = APP.read_bytes()
    need(sha256(code).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
    order = [0x169dc]+[0x16a30]*3+[0x16b50]*2+[0x16a30]*2
    for outcomes in product((0,1), repeat=8): need(follow(code,0,outcomes)==(order,0))
    need(follow(code,0,[0xffffffff]*8)==(order,0))
    need(follow(code,1,[])==([],1))
    changed = bytearray(code)
    changed[0xeef8:0xeefa] = bytes.fromhex('2a85')  # mv a0,a0 leaves last call's word intact
    need(follow(changed,0,[0]*7+[1])==(order,1))
    print('PASS: 256 binary patterns, all-ones words, entry timeout, wrong return-register control')
