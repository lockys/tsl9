"""Bounded algebra for the 0x16acc ingress slice; no CPU emulation."""
from hashlib import sha256
from pathlib import Path

IMAGE = Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')
EXPECTED = bytes.fromhex('8347110113f787010de7034641019d463d8a1307f6ff1377f70f63ece600034501019583a6860e05930551015d8defc0ef8c')

def check(condition, message):
    if not condition:
        raise ValueError(message)

def main():
    image = IMAGE.read_bytes()
    check(sha256(image).hexdigest() == '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667', 'image identity')
    check(image[0x16acc-0x8000:0x16afa+4-0x8000] == EXPECTED, 'instruction slice')
    lengths = [x for x in range(256) if (((x & 15) - 1) & 255) <= 7]
    check(len(lengths) == 128 and all(1 <= (x & 15) <= 8 for x in lengths), 'length domain')
    counts = [0] * 2048
    for byte0 in range(256):
        for byte1 in range(256):
            if not (byte1 & 0x18):
                counts[(byte0 << 3) | (byte1 >> 5)] += 1
    check(counts == [8] * 2048, 'ID domain or multiplicity')
    check((0x28 << 3 | 0xa0 >> 5) == 325, '325')
    check((0x73 << 3 | 0xa0 >> 5) == 925, '925')
    print('PASS: pinned slice; 2048 IDs x 8 header encodings; 128 length bytes')

if __name__ == '__main__':
    main()
