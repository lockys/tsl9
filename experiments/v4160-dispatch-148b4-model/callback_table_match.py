"""Matched-entry continuation 0x90cc..0x9110; synthetic memory and provider."""
import hashlib
from pathlib import Path

IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BASE, MASK = 0x2000be08, 0xffffffff


def run(image, index, payload, gp_byte, table=None):
    if not 0 <= index < 15 or not 0 <= payload <= MASK or not 0 <= gp_byte <= 255:
        raise ValueError('invalid projection input')
    # Original entry state after a successful scan; memory accesses are synthetic.
    r = [0] * 32
    r[2], r[3], r[8], r[9] = 0x20001ff0, 0x20001000, index, BASE
    stack = {r[2] + 4: 0x33333333, r[2] + 8: 0x22222222, r[2] + 12: 0x14800}
    entry = BASE + 12 * index
    memory = {entry + 4: 0x12345678, entry + 8: payload} if table is None else dict(table)
    if memory.get(entry + 8) != payload or entry + 4 not in memory:
        raise ValueError('selected entry does not match payload')
    calls, writes = [], []
    pc = 0x90cc
    for _ in range(40):
        if pc == 0x13572468:
            calls.append((pc, r[10]))
            # Provider may clobber caller-saved registers; callee-saved and sp survive.
            for reg in (5, 6, 7, 10, 11, 12, 13, 14, 15, 16, 17, 28, 29, 30, 31):
                r[reg] = (0xa5000000 + reg) & MASK
            pc = r[1]
            continue
        if pc == 0x24681356:
            return calls, writes, (r[10], r[11], r[1], r[2], r[8], r[9]), memory
        if not 0x90cc <= pc < 0x9110 or pc & 1: raise ValueError(f'unexpected PC {pc:#x}')
        off = pc - 0x8000
        h = int.from_bytes(image[off:off+2], 'little')
        if h & 3 != 3:
            if h == 0x47b1: r[15] = 12
            elif h == 0x97a6: r[15] = (r[15] + r[9]) & MASK
            elif h == 0x4788:
                address = (r[15] + 8) & MASK
                if address not in memory: raise ValueError('unexpected payload read')
                r[10] = memory[address]
            elif h == 0xc509:
                if r[10] == 0:
                    pc = 0x90e0
                    continue
            elif h == 0x57bc:
                if r[15] + 104 != 0x40068: raise ValueError('unexpected provider pointer')
                r[15] = 0x13572468
            elif h == 0x9782:
                target = r[15] & ~1
                r[1], pc = pc + 2, target
                continue
            elif h == 0x4585: r[11] = 1
            elif h == 0x4422: r[8] = stack[r[2]+8]
            elif h == 0x40b2: r[1] = stack[r[2]+12]
            elif h == 0x05c2: r[11] = (r[11] << 16) & MASK
            elif h == 0x81c1: r[11] >>= 16
            elif h == 0x94be: r[9] = (r[9] + r[15]) & MASK
            elif h == 0x4492: r[9] = stack[r[2]+4]
            elif h == 0x0141: r[2] += 16
            elif h == 0x8302:
                pc = r[6] & ~1
                continue
            else: raise ValueError(f'unsupported compressed instruction {h:#x} at {pc:#x}')
            pc += 2
        else:
            w = int.from_bytes(image[off:off+4], 'little')
            if w == 0x02f407b3: r[15] = (r[8] * r[15]) & MASK
            elif w == 0x008595b3: r[11] = (r[11] << (r[8] & 31)) & MASK
            elif w == 0x000407b7: r[15] = 0x40000
            elif w == 0x0a61c503: r[10] = gp_byte
            elif w in (0x0004a223, 0x0004a423):
                address = r[9] + (4 if w == 0x0004a223 else 8)
                if address not in memory: raise ValueError('unexpected table write')
                memory[address] = 0
                writes.append((address, 0))
            elif w == 0x05c7a303:
                if r[15] + 92 != 0x4005c: raise ValueError('unexpected tail pointer')
                r[6] = 0x24681356
            else: raise ValueError(f'unsupported instruction {w:#x} at {pc:#x}')
            pc += 4
    raise ValueError('instruction budget exceeded')


def main():
    image = IMAGE.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != SHA: raise ValueError('firmware identity mismatch')
    count = 0
    for index in range(15):
        for payload in (0, 1, 0xffffffff):
            for gp_byte in (0, 1, 255):
                calls, writes, regs, memory = run(image, index, payload, gp_byte)
                entry = BASE + 12 * index
                if calls != ([] if payload == 0 else [(0x13572468, payload)]): raise ValueError('provider call mismatch')
                if writes != [(entry + 4, 0), (entry + 8, 0)] or memory != {entry + 4: 0, entry + 8: 0}: raise ValueError('clear mismatch')
                if regs != (gp_byte, 1 << index, 0x14800, 0x20002000, 0x22222222, 0x33333333): raise ValueError('tail registers mismatch')
                count += 1
    mutant = bytearray(image)
    mutant[0x90fe - 0x8000] ^= 4
    try: run(mutant, 7, 1, 2)
    except ValueError: pass
    else: raise ValueError('table store mutation missed')
    print(f'PASS: {count} synthetic matched-entry cases; optional provider stub, two stores and tail arguments')


if __name__ == '__main__': main()
