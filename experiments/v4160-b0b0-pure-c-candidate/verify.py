"""Read-only identity and byte checks, not C execution or semantic proof."""
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMAGE = HERE.parents[1] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
IMAGE_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
C_SHA = '81dde947df04c123617fa2fa326ca7f2a78544b461fabbb8ba64ae5a1cd74a4a'
OFFSET = 0xb0b0 - 0x8000
WINDOW = bytes.fromhex('97 17 00 20 a3 8d a7 e2 82 80')


def check_window(image):
    if image[OFFSET:OFFSET + len(WINDOW)] != WINDOW:
        raise ValueError('instruction window mismatch or truncated')


def verify(image, candidate):
    if len(image) != 0x12c00 or sha256(image).hexdigest() != IMAGE_SHA:
        raise ValueError('image identity mismatch')
    check_window(image)
    if sha256(candidate).hexdigest() != C_SHA:
        raise ValueError('candidate identity mismatch')


if __name__ == '__main__':
    verify(IMAGE.read_bytes(), (HERE / 'leaf.c').read_bytes())
    print('image identity, instruction bytes and candidate identity verified (data only)')
