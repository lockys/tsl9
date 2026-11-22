"""Bounded replay of the APP RTC sampler against ordered synthetic bus reads."""
from hashlib import sha256
from pathlib import Path

APP = Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')
HI, LO = 0x40002818, 0x4000281c

def check(ok):
    if not ok:
        raise ValueError('RTC instruction or bus trace mismatch')

def run(code, reads):
    regs = [0] * 32
    pc, n = 0, 0
    for _ in range(100):
        check(0 <= pc < len(code) and not pc % 2)
        h = int.from_bytes(code[pc:pc+2], 'little')
        if h & 3 != 3:
            d = (h >> 7) & 31
            if h in (0x742, 0x7c2, 0x542): regs[d] = (regs[d] << 16) & 0xffffffff
            elif h in (0x8341, 0x83c1, 0x8141): regs[8 + (d & 7)] >>= 16
            elif h == 0x8d5d: regs[10] |= regs[15]
            elif h == 0x8082:
                check(n == len(reads)); return regs[10]
            else: raise ValueError('unknown short opcode')
            pc += 2; continue
        w = int.from_bytes(code[pc:pc+4], 'little')
        d, a, b = (w >> 7) & 31, (w >> 15) & 31, (w >> 20) & 31
        if w & 127 == 55: regs[d] = w & 0xfffff000
        elif w & 0x707f == 0x5003:
            addr = regs[a] + ((w >> 20 ^ 2048) - 2048)
            if n == len(reads): return ('waiting', addr)
            expected, regs[d] = reads[n]; n += 1
            check(addr == expected and 0 <= regs[d] <= 65535)
        elif w & 0x707f in (0x63, 0x1063):
            disp = ((w >> 31) << 12 | (w >> 7 & 1) << 11 | (w >> 25 & 63) << 5 | (w >> 8 & 15) << 1)
            if (regs[a] != regs[b]) == bool(w & 0x1000):
                pc += (disp ^ 4096) - 4096; continue
        else: raise ValueError('unknown long opcode')
        pc += 4
    raise ValueError('test budget')

if __name__ == '__main__':
    raw = APP.read_bytes()
    check(sha256(raw).hexdigest() == '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
    code = raw[0x111c6:0x11220]
    cases = 0
    for hi, final in [(0,0),(65535,65535),(0,1),(65535,0)]:
        groups = [(HI,hi),(LO,65535),(HI,final)] + ([(LO,7)] if hi != final else [])
        for retries in range(1 << len(groups)):
            reads = []
            for i,(addr,val) in enumerate(groups):
                if retries >> i & 1: reads += [(addr,val ^ 1),(addr,val)]
                reads += [(addr,val)] * 2
            expected_low = 7 if hi != final else 65535
            check(run(code,reads) == (final << 16 | expected_low))
            check(run(code,reads[:-1]) == ('waiting',reads[-1][0]))
            cases += 1
    print(f'PASS: {cases} ordered returns and {cases} incomplete traces')
