from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMAGE = HERE.parents[1] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
IMAGE_HASH = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
C_HASH = '4c2c5ec4778ae2f7c831a0e41cf332442006ef894a3175b2a6e7ea5e549ac7ea'
WINDOW = bytes.fromhex('b7066745 b7270240 93863612 3797efcd d4c3 1307b79a d8c3 d4d3 d8d3 8280')


def check(ok, message):
    if not ok:
        raise ValueError(message)


def pin_window(data):
    check(data[0x10e98:0x10eb6] == WINDOW, 'window bytes')


def pin_image(data):
    check(len(data) == 76800, 'image length')
    check(sha256(data).hexdigest() == IMAGE_HASH, 'image SHA')
    pin_window(data)


def pin_c(data):
    check(sha256(data).hexdigest() == C_HASH, 'C SHA')


def decode(lui, addi):
    check(lui & 0x7f == 0x37, 'not LUI')
    check(addi & 0x707f == 0x13, 'not ADDI')
    check((lui >> 7) & 31 == (addi >> 15) & 31 == (addi >> 7) & 31, 'register mismatch')
    imm = (addi >> 20) & 0xfff
    imm = imm - 0x1000 if imm & 0x800 else imm
    return ((lui & 0xfffff000) + imm) & 0xffffffff, imm


def reference(first, second, base):
    return [(base + 4, first), (base + 4, second),
            (base + 36, first), (base + 36, second)]


def rejected(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise RuntimeError('negative case accepted')


def main():
    image = IMAGE.read_bytes()
    source = (HERE / 'candidate.c').read_bytes()
    pin_image(image)
    pin_c(source)
    w = WINDOW
    word = lambda offset: int.from_bytes(w[offset:offset + 4], 'little')
    first, pos = decode(word(0), word(8))
    second, neg = decode(word(12), word(18))
    check((first, pos, second, neg) == (0x45670123, 291, 0xcdef89ab, -1621), 'decoded constants')
    check(word(4) == 0x400227b7, 'base LUI')
    base = word(4) & 0xfffff000
    check(reference(first, second, base) == [
        (0x40022004, 0x45670123), (0x40022004, 0xcdef89ab),
        (0x40022024, 0x45670123), (0x40022024, 0xcdef89ab)], 'events')
    changed = bytearray(image)
    changed[0x10e98] ^= 1
    rejected(pin_image, changed)
    rejected(pin_window, changed)
    changed = bytearray(image)
    changed[0] ^= 1
    rejected(pin_image, changed)
    rejected(pin_c, source + b' ')
    rejected(pin_image, image[:-1])
    check(decode(word(0), word(8) ^ (1 << 20))[0] == 0x45670122, 'positive immediate mutation')
    check(decode(word(12), word(18) ^ (1 << 20))[0] == 0xcdef89aa, 'negative immediate mutation')
    rejected(decode, word(0) ^ 1, word(8))
    rejected(decode, word(0), word(8) ^ (1 << 7))
    check(reference(first, second, base) != reference(second, first, base), 'event mutation')
    print('OK: pins, decode and Python reference; C not executed or verified')


if __name__ == '__main__':
    main()
