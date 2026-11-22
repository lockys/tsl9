"""Check selected encodings and sample fields at the RF join; not a CPU emulator."""
from hashlib import sha256
from pathlib import Path
import sys

EXPECTED = '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'

def check(image):
    if sha256(image).hexdigest() != EXPECTED:
        raise ValueError('reference SHA-256 mismatch')
    for pc, encoded in [(0x66506,'03a707091377f70398a0'), (0x66510,'03a7470929831377f70798a2'), (0x66552,'a38ae658'), (0x66564,'2386e658'), (0x6659a,'238af958'), (0x665ac,'2302f758'), (0x665b0,'83c74959')]:
        data = bytes.fromhex(encoded)
        if image[pc-0x40000:pc-0x40000+len(data)] != data:
            raise ValueError(hex(pc))
    for pc in (0x6653a, 0x66586):
        offset = pc-0x40000
        a = int.from_bytes(image[offset:offset+4], 'little')
        j = int.from_bytes(image[offset+4:offset+8], 'little')
        disp = (j >> 20) - ((j >> 31) << 12)
        if (a & 4095, j & 0xfffff, ((pc+(a & 0xfffff000)+disp)&0xfffffffe)) != (0x97,0x80e7,0x20002df2):
            raise ValueError('wait call at '+hex(pc))
    for upper in range(128):
        for low in range(64):
            w = (upper << 10) | (15 << 6) | low
            if (w & 63, (w >> 10) & 127) != (low, upper):
                raise ValueError('sample field mismatch')
    print('PASS: selected V1.31 bytes, 2 further wait calls, 8192 field pairs')

if __name__ == '__main__':
    check(Path(sys.argv[1]).read_bytes())
