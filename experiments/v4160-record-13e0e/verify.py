"""Limited original-byte execution of 0x13e0e with a1=1 and synthetic RAM."""
import hashlib
from pathlib import Path

BIN = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
MASK = 0xffffffff
FIRST, SECOND = 0x2000c796, 0x2000c79a


def sx(v, bits):
    return v - (1 << bits) if v & (1 << (bits-1)) else v


def run(image, handle, first, second, state=False):
    r = [0] * 32
    r[1], r[2], r[10], r[11] = 0x12345678, 0x20001000, handle, 1
    for reg in (8, 9, *range(18, 28)):
        r[reg] = 0xa5000000 | reg
    pc, reads, writes = 0x13e0e, [], []
    mem = {FIRST: first, SECOND: second}
    for _ in range(30):
        if pc == 0x12345678:
            return (reads, writes, tuple(r)) if state else (reads, writes)
        if not 0x13e0e <= pc < 0x13e98 or pc & 1: raise ValueError(f'bad PC {pc:#x}')
        off = pc - 0x8000
        h = int.from_bytes(image[off:off+2], 'little')
        if h & 3 != 3:
            if h == 0x4709: r[14] = 2
            elif h == 0x4705: r[14] = 1
            elif h == 0x4701: r[14] = 0
            elif h == 0x070a: r[14] = (r[14] << 2) & MASK
            elif h == 0x97ba: r[15] = (r[15] + r[14]) & MASK
            elif h == 0x8082:
                pc = r[1] & ~1
                continue
            elif h & 3 == 1 and h >> 13 == 5:
                imm = ((h >> 12 & 1) << 11 | (h >> 11 & 1) << 4 | (h >> 9 & 3) << 8 | (h >> 8 & 1) << 10 | (h >> 7 & 1) << 6 | (h >> 6 & 1) << 7 | (h >> 3 & 7) << 1 | (h >> 2 & 1) << 5)
                pc += sx(imm, 12)
                continue
            else: raise ValueError(f'unsupported compressed {h:#x} at {pc:#x}')
            pc += 2
        else:
            w = int.from_bytes(image[off:off+4], 'little')
            op, rd, f, a, b = w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31
            if op == 0x17: r[rd] = (pc + (w & 0xfffff000)) & MASK
            elif op == 0x13 and f == 0: r[rd] = (r[a] + sx(w >> 20, 12)) & MASK
            elif op == 3 and f == 5:
                address = (r[a] + sx(w >> 20, 12)) & MASK
                if address not in mem: raise ValueError('unexpected load')
                reads.append(address)
                r[rd] = mem[address]
            elif op == 0x23 and f == 0:
                imm = sx((w >> 25 << 5) | rd, 12)
                writes.append(((r[a] + imm) & MASK, r[b] & 255))
            elif op == 0x63 and f in (0, 1):
                imm = ((w >> 31 & 1) << 12 | (w >> 7 & 1) << 11 | (w >> 25 & 63) << 5 | (w >> 8 & 15) << 1)
                if (r[a] == r[b]) == (f == 0):
                    pc += sx(imm, 13)
                    continue
            else: raise ValueError(f'unsupported instruction {w:#x} at {pc:#x}')
            pc += 4
        r[0] = 0
    raise ValueError('instruction limit')


def main():
    image = BIN.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != SHA: raise ValueError('firmware identity mismatch')
    cases = 0
    for value in range(65536):
        for handle, first, second, reads, writes in (
            (value, value, value ^ 1, [FIRST], [(FIRST+2, 1), (FIRST+3, 0)]),
            (value, value ^ 1, value, [FIRST, SECOND], [(SECOND+2, 1), (SECOND+3, 0)]),
            (value, value, value, [FIRST], [(FIRST+2, 1), (FIRST+3, 0)]),
            (value, value ^ 1, value ^ 1, [FIRST, SECOND], []),
            (value | 0x10000, value, value, [FIRST, SECOND], []),
        ):
            if run(image, handle, first, second) != (reads, writes): raise ValueError(f'mismatch at {handle:#x}')
            cases += 1
    changed = bytearray(image)
    changed[0x13e32-0x8000+1] ^= 0x10
    try: actual = run(changed, 5, 5, 4)
    except ValueError: pass
    else:
        if actual == ([FIRST], [(FIRST+2, 1), (FIRST+3, 0)]): raise ValueError('branch mutant survived')
    print(f'PASS: {cases} synthetic cases; first-match priority, reads, ordered byte writes and branch mutant')
    print('Bounded a1=1 path only; successful memory operations, no concurrency or hardware.')


if __name__ == '__main__': main()
