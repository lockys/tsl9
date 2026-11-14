"""Decode the 0x14800 precheck for every possible successfully loaded halfword."""
import hashlib
from pathlib import Path

IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
MASK = 0xffffffff

def signed(x, n): return x - (1 << n) if x & (1 << (n - 1)) else x

def run(window, loaded, s0):
    if len(window) != 18 or not 0 <= loaded <= 65535 or not 0 <= s0 <= MASK:
        raise ValueError('invalid precheck input')
    x = [0] * 32; x[8] = s0; pc = 0x14800; address = None
    for _ in range(8):
        if pc in (0x1482e, 0x14838, 0x14848, 0x14812):
            return pc, address
        off = pc - 0x14800
        if off < 0 or off + 2 > len(window) or pc & 1:
            raise ValueError(f'outside precheck: {pc:#x}')
        h = int.from_bytes(window[off:off+2], 'little')
        if h & 3 != 3:
            q, f3, rd = h & 3, h >> 13, (h >> 7) & 31
            if q == 1 and f3 == 3 and rd not in (0, 2):  # C.LUI
                imm = signed((h >> 2 & 31) | ((h >> 12 & 1) << 5), 6)
                x[rd] = (imm << 12) & MASK; pc += 2
            elif q == 1 and f3 == 7:  # C.BNEZ
                rs1 = 8 + (h >> 7 & 7)
                imm = ((h >> 12 & 1) << 8 | (h >> 10 & 3) << 3 | (h >> 5 & 3) << 6 |
                       (h >> 3 & 3) << 1 | (h >> 2 & 1) << 5)
                pc = pc + signed(imm, 9) if x[rs1] else pc + 2
            else: raise ValueError(f'unsupported compressed instruction {h:#x} at {pc:#x}')
        else:
            if off + 4 > len(window): raise ValueError('truncated precheck instruction')
            w = int.from_bytes(window[off:off+4], 'little')
            op, rd, f3, rs1, rs2 = w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31
            if op == 3 and f3 == 5:  # LHU, externally supplied successful read
                address = (x[rs1] + signed(w >> 20, 12)) & MASK
                x[rd] = loaded; pc += 4
            elif op == 0x63 and f3 == 0:  # BEQ
                imm = ((w >> 31 & 1) << 12 | (w >> 7 & 1) << 11 | (w >> 25 & 63) << 5 | (w >> 8 & 15) << 1)
                pc = pc + signed(imm, 13) if x[rs1] == x[rs2] else pc + 4
            else: raise ValueError(f'unsupported instruction {w:#x} at {pc:#x}')
        x[0] = 0
    raise ValueError('precheck instruction limit exceeded')

def main():
    data = IMAGE.read_bytes()
    if len(data) != 76800 or hashlib.sha256(data).hexdigest() != SHA:
        raise ValueError('firmware identity mismatch')
    window = data[0x14800-0x8000:0x14812-0x8000]
    if window != bytes.fromhex('8357240005676384e70209676386e70285ef'):
        raise ValueError('precheck bytes mismatch')
    counts = {}
    for value in range(65536):
        expected = 0x14812 if value == 0 else 0x1482e if value == 0x1000 else 0x14838 if value == 0x2000 else 0x14848
        pc, addr = run(window, value, 0xfffffffe)
        if pc != expected or addr != 0:
            raise ValueError(f'precheck mismatch for {value:#x}: {pc:#x}, {addr!r}')
        counts[pc] = counts.get(pc, 0) + 1
    if counts != {0x14812: 1, 0x1482e: 1, 0x14838: 1, 0x14848: 65533}:
        raise ValueError(f'bad destination counts: {counts}')
    mutant = bytearray(window); mutant[6] = 0
    try: run(mutant, 0x1000, 0)
    except ValueError: pass
    else: raise ValueError('invalid opcode mutation accepted')
    print('PASS: all 65536 LHU values decoded; zero/0x1000/0x2000 separated; 65533 reach 0x14848')

if __name__ == '__main__': main()
