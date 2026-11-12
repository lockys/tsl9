"""Read-only firmware identity and fixed byte window checks; no C execution."""
import hashlib
from pathlib import Path

IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
SIZE = 76800
START = 0xb0b0 - 0x8000
WINDOW = bytes.fromhex('97 17 00 20 a3 8d a7 e2 82 80')
SOURCE_DIR = Path(__file__).resolve().parent
SOURCE_SHA256 = {
    'leaf.c': '125459d53d0c9a111b2f28d7b5949b9945b64de777fc13403b5fb2849dadee56',
    'leaf.h': '4c16e55b67d349cd1fbc04aaeeb01d299239cf934eb4f53ecdd1cdd90daf4e77',
    'host_harness.c': '30fc6866a3ba570413a88d2f3b011c60c009f2397f2ba709f3472693d2a5a9c3',
}


def check_sources(directory=SOURCE_DIR):
    for name, expected in SOURCE_SHA256.items():
        if hashlib.sha256((directory / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'source identity mismatch: {name}')


def check_window(data):
    if len(data) < START + len(WINDOW) or data[START:START + len(WINDOW)] != WINDOW:
        raise ValueError('instruction window mismatch')


def check_image(data):
    if len(data) != SIZE or hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError('firmware identity mismatch')
    check_window(data)


if __name__ == '__main__':
    check_image(IMAGE.read_bytes())
    check_sources()
    print('firmware identity and window, source identities OK')
