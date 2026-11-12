#!/usr/bin/env python3
"""Read-only static evidence for one pinned image; no target instruction execution."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
BASE = 0x8000
SIZE = 76800
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
WINDOWS = {
    # GP setup, copy and clear, including both unsigned branches.
    0x186aa: bytes.fromhex('97c1fe1f938161951781ff1f1301e194172500001305654a938501001386010863fac5008322050023a0550011059105e3eac5fe138501089745ff1f938565276377b500232005001105e36db5fe'),
    0x1ab60: bytes.fromhex('020000000c0004000100000038ab010002000000120004000100000042ab01000200000044ab010002000000884000200200000018000400030000008040002000000000000000000102030406070809000001009cc200200cc300200cc4002094c4002094c5002094c6002000d8b805a90089018c060000ea037a03a1030000'),
    0x167a6: bytes.fromhex('011122cc26ca4ac84ec606ce52c456c2aa840144938901061309e00f83a70900a29703c707006316970003c51700efe0dfdf0904e31424ff9d4a054493894106138a81061309400203a709005697834607000347170093771700a207d58f63989700098b09c7a2850145ef10a01703270a005697834607000347170093771700a207d58f6398f400098b09c7a2850545ef10401505041374f40f9d0ae31624fb'),
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def check_windows(data):
    for address, expected in WINDOWS.items():
        start = address - BASE
        require(data[start:start + len(expected)] == expected, 'window mismatch at %#x' % address)


def check_image(data):
    require(len(data) == SIZE, 'image size mismatch')
    require(hashlib.sha256(data).hexdigest() == SHA, 'image SHA-256 mismatch')
    check_windows(data)


def derive(data):
    # Arithmetic on the audited fixed constants, not execution or simulation.
    gp, src, length, clear_end = 0x20004000, 0x1ab60, 128, 0x2000c958
    copy_end = gp + length
    require(length % 4 == 0 and (clear_end - copy_end) % 4 == 0, 'unaligned bounds')
    require(gp < copy_end <= clear_end, 'invalid bounds')
    slots = []
    for offset in (0x60, 0x64, 0x68):
        raw = data[src - BASE + offset:src - BASE + offset + 4]
        require(len(raw) == 4, 'truncated slot')
        slots.append(int.from_bytes(raw, 'little'))
    require(slots == [0x2000c494, 0x2000c594, 0x2000c694], 'slot mismatch')
    first = list(range(0, 254, 2))
    second = [7 * i for i in range(1, 36)]
    require((len(first), first[0], first[-1]) == (127, 0, 252), 'first range')
    require((len(second), second[0], second[-1]) == (35, 7, 245), 'second range')
    return gp, copy_end, clear_end, slots, first, second


def rejected(fn, data, label):
    try:
        fn(data)
    except ValueError:
        return
    raise ValueError('malformed fixture accepted: ' + label)


def self_test(data):
    rejected(check_image, data[:-1], 'truncation')
    rejected(check_image, data + b'\0', 'extension')
    changed = bytearray(data)
    changed[0] ^= 1
    rejected(check_image, changed, 'outside-window hash')
    for address, expected in WINDOWS.items():
        for i in range(len(expected)):
            changed = bytearray(data)
            changed[address - BASE + i] ^= 1
            rejected(check_windows, changed, 'window byte %#x' % (address + i))
        rejected(check_windows, data[:address - BASE + len(expected) - 1], 'window truncation')
    bad = bytearray(data)
    bad[0x1abc0 - BASE] ^= 1
    rejected(derive, bad, 'initializer word')
    rejected(derive, data[:0x1abc8 - BASE], 'truncated initializer')


def main():
    data = IMAGE.read_bytes()
    check_image(data)
    gp, copy_end, clear_end, slots, first, second = derive(data)
    self_test(data)
    print('OK: pinned image, exact reset/initializer/table windows and malformed fixtures')
    print('conditional copy [%#x,%#x), clear [%#x,%#x): %d and %d words' %
          (gp, copy_end, copy_end, clear_end, (copy_end-gp)//4, (clear_end-copy_end)//4))
    for slot, value in zip((gp+0x60, gp+0x64, gp+0x68), slots):
        print('slot %#x <- %#x' % (slot, value))
    print('first offsets key %d..%d step 2; conditional value +1' % (first[0], first[-1]))
    print('other offsets %d..%d step 7; high +1' % (second[0], second[-1]))


if __name__ == '__main__':
    main()
