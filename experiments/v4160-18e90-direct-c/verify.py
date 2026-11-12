"""Offline byte pins only; does not compile, run, or test C behavior."""
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BIN = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
IMAGE_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
SOURCE_SHA = 'a2a291bc18c69ec4911de3e46149234e9d968ea2fac0f5df3180edb180aa0536'
START = 0x18e90 - 0x8000
WINDOW = bytes.fromhex('b7270240c8c78280')


def check(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return sha256(data).hexdigest()


def check_length(image):
    check(len(image) == 76800, 'image length')


def check_image_hash(image):
    check(digest(image) == IMAGE_SHA, 'image hash')


def check_window(image):
    check(image[START:START + len(WINDOW)] == WINDOW, 'window bytes')


def check_source(source):
    check(digest(source) == SOURCE_SHA, 'source hash')


def rejects(fn, data):
    try:
        fn(data)
    except ValueError:
        return
    raise ValueError('negative case accepted: ' + fn.__name__)


def main():
    image = BIN.read_bytes()
    source = (HERE / 'candidate.c').read_bytes()
    check_length(image)
    check_image_hash(image)
    check_window(image)
    check_source(source)
    changed = bytearray(image)
    changed[START] ^= 1
    rejects(check_length, image[:-1])
    rejects(check_image_hash, changed)
    rejects(check_window, changed)
    rejects(check_window, image[:START + len(WINDOW) - 1])
    rejects(check_source, source + b'\n')
    print('OK: static pins and negative cases only; C behavior untested')


if __name__ == '__main__':
    main()
