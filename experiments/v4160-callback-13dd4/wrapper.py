"""Execute bounded callback bytes using explicit, synthetic callee stubs."""
import hashlib
from verify import BIN, SHA, CODE, BASE, jal_target, bnez_target

MASK = 0xffffffff


def run(code, queue, ra, sp, first_return, second_return):
    if len(code) != len(CODE) or not all(0 <= x <= MASK for x in (queue, ra, sp, first_return, second_return)):
        raise ValueError('invalid inputs')
    r = [0] * 32
    r[1], r[2], r[10] = ra, sp, 0xdeadbeef
    memory, calls = {}, []
    pc = BASE
    for _ in range(30):
        if pc == (ra & ~1):
            return 'return', r[2], calls
        off = pc - BASE
        if off < 0 or off+2 > len(code) or pc & 1: raise ValueError('PC outside wrapper')
        h = int.from_bytes(code[off:off+2], 'little')
        if h & 3 != 3:
            if h == 0x1141: r[2] = (r[2]-16) & MASK
            elif h == 0xc606: memory[(r[2]+12) & MASK] = r[1]
            elif h == 0x4501: r[10] = 0
            elif h == 0x4681: r[13] = 0
            elif h == 0x4581: r[11] = 0
            elif h == 0x40b2:
                address = (r[2]+12) & MASK
                if address not in memory: raise ValueError('missing saved return')
                r[1] = memory[address]
            elif h == 0x0141: r[2] = (r[2]+16) & MASK
            elif h == 0x8082:
                pc = r[1] & ~1
                continue
            elif h & 3 == 1 and h >> 13 == 7:
                target = bnez_target(pc, h)
                if r[10] != 0:
                    pc = target
                    continue
            else: raise ValueError(f'unsupported compressed {h:#x} at {pc:#x}')
            pc += 2
        else:
            if off + 4 > len(code): raise ValueError('truncated instruction')
            w = int.from_bytes(code[off:off+4], 'little')
            if w == 0x00000517: r[10] = pc
            elif w == 0xffe50513: r[10] = (r[10]-2) & MASK
            elif w == 0x12c00613: r[12] = 300
            elif w == 0x18e50513: r[10] = (r[10]+398) & MASK
            elif w & 127 == 0x6f:
                rd = w >> 7 & 31
                if rd not in (0, 1): raise ValueError('invalid JAL destination register')
                dest = jal_target(pc, w, rd)
                calls.append((dest, tuple(r[i] for i in (10, 11, 12, 13))))
                if rd == 0:
                    return 'tail', r[2], calls
                if dest not in (0x90b0, 0x13d48, 0x81aa): raise ValueError('unknown callee')
                r[1] = pc+4
                # Each stub is assumed to return normally; only a0 is varied.
                r[10] = {0x90b0: first_return, 0x13d48: second_return, 0x81aa: queue}[dest]
            else: raise ValueError(f'unsupported word {w:#x} at {pc:#x}')
            pc += 4
    raise ValueError('instruction limit')


def main():
    image = BIN.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != SHA: raise ValueError('firmware identity mismatch')
    code = image[BASE-0x8000:BASE-0x8000+len(CODE)]
    if code != CODE: raise ValueError('callback bytes mismatch')
    count = 0
    for queue in range(256):
        for sp in (0, 0x20001000, 0xfffffff0):
            for first in (0, 0xffffffff):
                for second in (0, 0x87654321):
                    kind, final_sp, calls = run(code, queue, 0x10000101, sp, first, second)
                    if final_sp != sp or [c[0] for c in calls[:3]] != [0x90b0, 0x13d48, 0x81aa]: raise ValueError('frame or calls')
                    if calls[0][1][0] != BASE or calls[1][1][0] != 0: raise ValueError('arguments')
                    if queue:
                        if kind != 'return' or len(calls) != 3: raise ValueError('nonzero route')
                    elif kind != 'tail' or len(calls) != 4 or calls[3] != (0x9124, (0x13f88, 0, 300, 0)):
                        raise ValueError('zero route')
                    count += 1
    reference = run(code, 0, 0x10000101, 0x20001000, 0, 0)
    for offset, bit in ((0x1b, 0x20), (0x20, 1), (0x0e, 0x20)):
        mutated = bytearray(code)
        mutated[offset] ^= bit
        try:
            actual = run(mutated, 0, 0x10000101, 0x20001000, 0, 0)
        except ValueError:
            continue
        if actual == reference: raise ValueError(f'mutant {offset:#x} survived')
    print(f'PASS: {count} synthetic callback traces; frame restore, ordered calls, queue exit and three mutants')
    print('All three external calls are returning stubs; no table effects or hardware execution.')


if __name__ == '__main__': main()
