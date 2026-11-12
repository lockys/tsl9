"""Finite, conditional byte-memory events; not an instruction emulator."""
import hashlib
from pathlib import Path

MASK = 0xffffffff
BASE = 0x2000c29c
IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
WINDOW = bytes.fromhex('411126c2b7040400bc4422c41794ff1f1304641206c6228513060007814582978567fd172311f40085472302f400930710102314f400938741058843fc441146977500009385254f31058297')


def check_window(data):
    if data[0x1316a - 0x8000:0x1316a - 0x8000 + len(WINDOW)] != WINDOW:
        raise ValueError('instruction window mismatch')


def check_image(data):
    if len(data) != 0x12c00 or hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError('image size or digest mismatch')
    check_window(data)


class Memory:
    """Sparse initialized bytes; accesses wrap modulo 2**32, no implicit zero."""
    def __init__(self):
        self.bytes = {}

    def store(self, address, value, width):
        if width not in (1, 2, 4) or address & (width - 1):
            raise ValueError('unsupported width or unaligned store')
        if not 0 <= value < 1 << (8 * width):
            raise ValueError('value outside width')
        for i in range(width):
            self.bytes[(address + i) & MASK] = (value >> (8 * i)) & 255

    def load(self, address, width):
        if width not in (1, 2, 4) or address & (width - 1):
            raise ValueError('unsupported width or unaligned load')
        return sum(self.bytes[(address + i) & MASK] << (8 * i) for i in range(width))


def events(mem, gp, earlier_callee):
    """First indirect call has returned; callback describes its memory effects.

    Inputs assume s0=BASE, s1=0x40000, gp and sp preserved, valid stack,
    no asynchronous writes, and all touched bytes ordinary readable/writable RAM.
    Callback returns normally; its target is outside this model.
    """
    first_target = mem.load(0x40048, 4) & ~1
    earlier_callee(mem)
    mem.store(BASE + 2, 0x0fff, 2)
    mem.store(BASE + 4, 1, 1)
    mem.store(BASE + 8, 0x0101, 2)
    address = (gp + 84) & MASK
    pointer = mem.load(address, 4)
    second_target = mem.load(0x4004c, 4) & ~1
    return first_target, address, pointer, second_target, (pointer + 12) & MASK
