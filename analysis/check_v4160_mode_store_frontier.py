"""Read-only APP control/operand check. Pass the decoded v4.1.60 BIN as argv[1]."""
import hashlib
import sys
from pathlib import Path


def check(blob):
    if hashlib.sha256(blob).hexdigest() != '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667':
        raise ValueError('unexpected APP')

    def word(pc):
        return int.from_bytes(blob[pc-0x8000:pc-0x8000+4], 'little')

    def signed(n, bits):
        return (n ^ (1 << (bits-1))) - (1 << (bits-1))

    for pc, target in [(0x10754, 0xd272), (0x10758, 0xb0fc), (0x1075e, 0x820c), (0x10762, 0x10032)]:
        w = word(pc)
        imm = (w >> 31) << 20 | ((w >> 12) & 255) << 12 | ((w >> 20) & 1) << 11 | ((w >> 21) & 1023) << 1
        if w & 4095 != 0xef or pc + signed(imm, 21) != target:
            raise ValueError(f'call at {pc:x}')

    for pc, expected in [(0x10752, '2a84'), (0x1075c, '0145'), (0x10766, '1375f40f'), (0xb106, '22c41384010c'), (0xb118, 'a300f400'), (0xb136, '2244'), (0x8212, '9387010caa97a3800700')]:
        data = bytes.fromhex(expected)
        if blob[pc-0x8000:pc-0x8000+len(data)] != data:
            raise ValueError(f'operand window at {pc:x}')

    for pc, source, address in [(0x1076a, 0, 0x2000bfb4), (0x10772, 10, 0x2000bfb5)]:
        hi, st = word(pc), word(pc+4)
        offset = signed(((st >> 25) << 5) | ((st >> 7) & 31), 12)
        if hi & 4095 != 0x797 or st & 0x707f != 0x23 or (st >> 15) & 31 != 15 or (st >> 20) & 31 != source or (pc + (hi & 0xfffff000) + offset) & 0xffffffff != address:
            raise ValueError(f'store at {pc+4:x}')
    print('PASS: image hash; 4 direct calls; 7 operand windows; 2 byte stores')


if __name__ == '__main__':
    check(Path(sys.argv[1]).read_bytes())
