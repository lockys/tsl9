"""Offline: compare three live-destination copy sites with persistence snapshot sources."""
import hashlib
from pathlib import Path
import sys


def check(image):
    if hashlib.sha256(image).hexdigest() != '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667':
        raise ValueError('unexpected APP')
    def word(pc):
        return int.from_bytes(image[pc-0x8000:pc-0x8000+4], 'little')
    for slot, setup, call, wrapper, pair in (
        (96,0x14b08,0x14b1a,0x12e54,0x12e66),
        (100,0x14c10,0x14c20,0x12f48,0x12f5a),
        (104,0x14be4,0x14bf4,0x13052,0x13064),
    ):
        if word(setup) != (slot<<20 | 0x18713) or word(call)&65535 != 0x9782:
            raise ValueError('live slot or copy call')
        j = word(call+2)
        delta = -(j>>31)*0x100000 + ((j>>12&255)<<12) + ((j>>20&1)<<11) + ((j>>21&1023)<<1)
        if j&4095 != 0xef or call+2+delta != wrapper:
            raise ValueError('no direct wrapper call')
        hi, lo = word(pair), word(pair+4)
        if hi&4095 != 0x597 or lo&0xfffff != 0x58593:
            raise ValueError('not AUIPC/ADDI a1')
        fixed = (pair+(hi&0xfffff000)+(lo>>20)-(lo>>31)*4096)&0xffffffff
        reset = word(0x1ab60+slot)
        if fixed != reset: raise ValueError('not reset binding')
        print(f'gp+{slot}: copy call {call:#x}, snapshot source {fixed:#x} equals reset pointer')


if __name__ == '__main__': check(Path(sys.argv[1]).read_bytes())
