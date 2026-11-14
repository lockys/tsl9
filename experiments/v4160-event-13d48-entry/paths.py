"""Finite interpreter of 0x13d64-0x13d88 and direct-return epilogue.

Inputs are values observed at individual successful loads after the earlier
callee returns. This deliberately does not execute that callee.
"""
import hashlib
from pathlib import Path

BIN = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
# Exact permitted encodings. This is a fixed-window interpreter, not a general ISA decoder.
OPS = {
    0x13d64: '6387e600', 0x13d68: '03c75700', 0x13d6c: '1377f70f',
    0x13d70: '01cf', 0x13d72: '83d66700', 0x13d76: '4167',
    0x13d78: '7917', 0x13d7a: '630ad704', 0x13d7e: '83c79700',
    0x13d82: '93f7f70f', 0x13d86: 'a1e7', 0x13d88: '09cd',
    0x13dce: 'b240', 0x13dd0: '4101', 0x13dd2: '8280',
}


def run(image, h0, m0, h1, m1, result, sp, ra):
    if not (0 <= h0 <= 65535 and 0 <= h1 <= 65535 and 0 <= m0 <= 255 and 0 <= m1 <= 255):
        raise ValueError('read out of range')
    pc, a0, a3, a4, a5 = 0x13d64, result, h0, 0xfffe, 0x2000c794
    saved = {(sp-4) & 0xffffffff: ra}
    # JAL set ra to 0x13d50; a normal callee returns through that value.
    ra = 0x13d50
    sp = (sp-16) & 0xffffffff
    reads = [0x2000c796]
    for _ in range(16):
        if pc in (0x13da2, 0x13d8a): return pc, a0, sp, ra, tuple(reads)
        expected = bytes.fromhex(OPS[pc])
        off = pc-0x8000
        if image[off:off+len(expected)] != expected: raise ValueError(f'opcode mismatch {pc:#x}')
        if pc == 0x13d64: pc = 0x13d72 if a3 == a4 else 0x13d68
        elif pc == 0x13d68: reads.append(a5+5); a4 = m0; pc += 4
        elif pc == 0x13d6c: a4 &= 255; pc += 4
        elif pc == 0x13d70: pc = 0x13d88 if a4 == 0 else 0x13d72
        elif pc == 0x13d72: reads.append(a5+6); a3 = h1; pc += 4
        elif pc == 0x13d76: a4 = 0x10000; pc += 2
        elif pc == 0x13d78: a4 -= 2; pc += 2
        elif pc == 0x13d7a: pc = 0x13dce if a4 == a3 else 0x13d7e
        elif pc == 0x13d7e: reads.append(a5+9); a5 = m1; pc += 4
        elif pc == 0x13d82: a5 &= 255; pc += 4
        elif pc == 0x13d86: pc = 0x13dce if a5 else 0x13d88
        elif pc == 0x13d88: pc = 0x13da2 if a0 == 0 else 0x13d8a
        elif pc == 0x13dce: ra = saved[(sp+12) & 0xffffffff]; pc += 2
        elif pc == 0x13dd0: sp = (sp+16) & 0xffffffff; pc += 2
        elif pc == 0x13dd2: return ra, a0, sp, ra, tuple(reads)
    raise ValueError('instruction limit')


def main():
    image = BIN.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != SHA: raise ValueError('firmware identity mismatch')
    count, reached = 0, set()
    for h0 in (0xfffe, 0x1234):
        for m0 in range(256):
            for h1 in (0xfffe, 0x1234):
                for m1 in range(256):
                    for result in (0, 1):
                        reads = [0x2000c796]
                        direct = False
                        if h0 != 0xfffe:
                            reads.append(0x2000c799)
                        if h0 != 0xfffe and m0 == 0:
                            pass
                        else:
                            reads.append(0x2000c79a)
                            if h1 == 0xfffe: direct = True
                            else:
                                reads.append(0x2000c79d)
                                direct = m1 != 0
                        expected_pc = 0xabcdef00 if direct else (0x13da2 if result == 0 else 0x13d8a)
                        out = run(image, h0, m0, h1, m1, result, 0x20001000, 0xabcdef00)
                        expected_sp = 0x20001000 if direct else 0x20000ff0
                        expected_ra = 0xabcdef00 if direct else 0x13d50
                        if out != (expected_pc, result, expected_sp, expected_ra, tuple(reads)):
                            raise ValueError(f'path mismatch: {h0} {m0} {h1} {m1} {result}')
                        reached.add(expected_pc)
                        count += 1
    if reached != {0xabcdef00, 0x13da2, 0x13d8a}: raise ValueError('missing exit')
    # Exercise every allowed encoding by paths, and ensure changed encodings are rejected.
    tests = [(0x1234, 0, 0, 0, 0), (0xfffe, 0, 0xfffe, 0, 0), (0xfffe, 0, 0, 0, 1), (0xfffe, 0, 0, 1, 1)]
    for address, hexop in OPS.items():
        mutated = bytearray(image); mutated[address-0x8000] ^= 1
        caught = False
        for args in tests:
            try: run(mutated, *args, 0x20001000, 0xabcdef00)
            except ValueError as e:
                if str(e).startswith('opcode mismatch'): caught = True; break
        if not caught: raise ValueError(f'mutant not reached/rejected: {address:#x}')
    print(f'PASS: {count} traces, 3 exits, exact lazy read order, {len(OPS)} opcode mutations rejected')
    print('Post-call synthetic loads only; callee side effects, concurrency and hardware are not executed.')


if __name__ == '__main__': main()
