"""Original 0x13d48 entry through first conditional, with one callee stub."""
import hashlib
from pathlib import Path

BIN = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BASE, STOP_FALLTHROUGH, STOP_TAKEN = 0x13d48, 0x13d68, 0x13d72
CODE = bytes.fromhex('41 11 06 c6 ef f0 bf 89 41 67 97 96 ff 1f 83 d6 46 a4 79 17 97 97 ff 1f 93 87 87 a3 63 87 e6 00')
MASK = 0xffffffff


def sx(x, bits): return x - (1 << bits) if x & (1 << (bits-1)) else x


def run(code, before, after, result, sp, ra):
    if len(code) != len(CODE): raise ValueError('invalid window size')
    x = [0] * 32
    x[1], x[2], x[10] = ra, sp, 0
    memory = {0x2000c796: before}
    saved, calls, reads = {}, [], []
    pc = BASE
    for _ in range(12):
        if pc in (STOP_FALLTHROUGH, STOP_TAKEN):
            return pc, tuple(x), saved, calls, reads
        off = pc-BASE
        if off < 0 or off+2 > len(code) or pc & 1: raise ValueError('unexpected PC')
        h = int.from_bytes(code[off:off+2], 'little')
        if h & 3 != 3:
            if h == 0x1141: x[2] = (x[2]-16) & MASK
            elif h == 0xc606: saved[(x[2]+12) & MASK] = x[1]
            elif h == 0x6741: x[14] = 0x10000
            elif h == 0x1779: x[14] = (x[14]-2) & MASK
            else: raise ValueError(f'unsupported compressed {h:#x}')
            pc += 2
            continue
        if off+4 > len(code): raise ValueError('truncated')
        w = int.from_bytes(code[off:off+4], 'little')
        op, rd, f, r1, r2 = w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31
        if op == 0x6f and rd == 1:
            imm = ((w >> 31 & 1) << 20 | (w >> 12 & 255) << 12 | (w >> 20 & 1) << 11 | (w >> 21 & 1023) << 1)
            target = (pc + sx(imm, 21)) & MASK
            if target != 0x135e6: raise ValueError('unexpected callee')
            calls.append((target, x[10]))
            x[1] = pc+4
            # The returning stub may modify shared RAM before the caller reloads it.
            memory[0x2000c796], x[10] = after, result
        elif op == 0x17: x[rd] = (pc + (w & 0xfffff000)) & MASK
        elif op == 0x13 and f == 0: x[rd] = (x[r1] + sx(w >> 20, 12)) & MASK
        elif op == 3 and f == 5:
            address = (x[r1] + sx(w >> 20, 12)) & MASK
            if address not in memory: raise ValueError('unexpected load')
            reads.append(address)
            x[rd] = memory[address]
        elif op == 0x63 and f == 0:
            imm = ((w >> 31 & 1) << 12 | (w >> 7 & 1) << 11 | (w >> 25 & 63) << 5 | (w >> 8 & 15) << 1)
            if x[r1] == x[r2]:
                pc += sx(imm, 13)
                continue
        else: raise ValueError(f'unsupported instruction {w:#x}')
        x[0] = 0
        pc += 4
    raise ValueError('instruction limit')


def main():
    image = BIN.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != SHA: raise ValueError('firmware identity mismatch')
    code = image[BASE-0x8000:BASE-0x8000+len(CODE)]
    if code != CODE: raise ValueError('entry window mismatch')
    count = 0
    for after in range(65536):
        for result in (0, 0xffffffff):
            before, sp, ra = after ^ 1, 0x20001000, 0x12345678
            pc, x, saved, calls, reads = run(code, before, after, result, sp, ra)
            if (pc != (STOP_TAKEN if after == 0xfffe else STOP_FALLTHROUGH) or
                (x[10], x[13], x[14], x[15], x[2]) != (result, after, 0xfffe, 0x2000c794, sp-16) or
                saved != {sp-4: ra} or calls != [(0x135e6, 0)] or reads != [0x2000c796]):
                raise ValueError(f'mismatch after={after:#x}, result={result:#x}')
            count += 1
    altered = bytearray(code)
    altered[0x1e] ^= 0x10
    try: observed = run(altered, 0, 0xfffe, 0, 0x20001000, 0x12345678)[0]
    except ValueError: pass
    else:
        if observed == STOP_TAKEN: raise ValueError('branch mutant survived')
    print(f'PASS: {count} entry traces; post-call halfword reload, saved ra, callee result, both branch outcomes and mutation')
    print('The callee is a returning stub and may change the halfword; later branches and hardware are not executed.')


if __name__ == '__main__': main()
