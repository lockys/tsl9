"""Decode s2 arithmetic around one assumed-returning indirect call."""
import hashlib
from pathlib import Path

IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
MASK = 0xffffffff

def run(raw, initial):
    if len(raw) != 20 or not isinstance(initial, int) or not 0 <= initial <= MASK:
        raise ValueError('invalid length-bound input')
    # Inspect the specific register fields and immediates; other setup instructions
    # and the indirect callee itself are outside this projection.
    add = int.from_bytes(raw[0:2], 'little')
    if (add & 3, add >> 13, add >> 7 & 31) != (1, 0, 18):
        raise ValueError('expected C.ADDI s2')
    imm = (add >> 2 & 31) | ((add >> 12 & 1) << 5)
    if imm & 32: imm -= 64
    value = (initial + imm) & MASK
    shift = int.from_bytes(raw[8:10], 'little')
    if (shift & 3, shift >> 13, shift >> 7 & 31, shift >> 12 & 1) != (2, 0, 18, 0):
        raise ValueError('expected RV32 C.SLLI s2')
    value = (value << (shift >> 2 & 31)) & MASK
    call = int.from_bytes(raw[10:12], 'little')
    if call != 0x9782: raise ValueError('expected C.JALR a5')
    # Assumption: the target returns normally and preserves callee-saved s2.
    for off in (12, 16):
        w = int.from_bytes(raw[off:off+4], 'little')
        if (w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31, w >> 25) != (0x13, 18, 5, 18, 0):
            raise ValueError('expected SRLI s2,s2')
        value >>= (w >> 20) & 31
    return value

def main():
    data = IMAGE.read_bytes()
    if len(data) != 76800 or hashlib.sha256(data).hexdigest() != SHA:
        raise ValueError('firmware identity mismatch')
    raw = data[0x1486a-0x8000:0x1487e-0x8000]
    if raw != bytes.fromhex('7919314648108145420982971359090113591900'):
        raise ValueError('length-bound bytes mismatch')
    high_bounds = 0
    for value in (*range(65536), 0x10000, 0x10001, 0x7fffffff, 0x80000000, 0xffffffff):
        expected = ((value - 2) & 65535) >> 1
        decoded = run(raw, value)
        if decoded != expected:
            raise ValueError(f'length-bound mismatch at {value:#x}')
        if value <= 65535:
            high = decoded > 255
            if high != (value in (0, 1) or value >= 514):
                raise ValueError(f'high-bound threshold mismatch at {value:#x}')
            high_bounds += high
    if high_bounds != 65024:
        raise ValueError(f'incorrect high-bound count: {high_bounds}')
    if tuple(run(raw, x) for x in (0, 1, 2, 512, 513, 514)) != (32767, 32767, 0, 255, 255, 256):
        raise ValueError('missing length-underflow or high-bound boundary')
    altered = bytearray(raw); altered[0] ^= 4
    if run(altered, 21) == run(raw, 21):
        raise ValueError('C.ADDI immediate mutation not detected')
    print('PASS: 65536 lengths plus five RV32 edges; 65024 bounds >255 (0, 1, or >=514), under stated call assumption')
if __name__ == '__main__': main()
