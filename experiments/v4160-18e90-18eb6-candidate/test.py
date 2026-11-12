"""Static byte decoding and Python event model only; does not test C."""
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BIN = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'

def check(condition, message):
    if not condition:
        raise ValueError(message)

def digest(b):
    return sha256(b).hexdigest()

def decode(data):
    result = []
    pos = 0
    while pos < len(data):
        check(pos + 2 <= len(data), 'truncated')
        h = int.from_bytes(data[pos:pos + 2], 'little')
        if h & 3 == 3:
            check(pos + 4 <= len(data), 'truncated')
            w = int.from_bytes(data[pos:pos + 4], 'little')
            check(w & 0x7f == 0x37, 'unsupported 32-bit opcode')
            result.append(('lui', (w >> 7) & 31, w & 0xfffff000))
            pos += 4
            continue
        funct = h >> 13
        if h == 0x8082:
            result.append(('ret',))
        elif h & 3 == 0 and funct in (2, 6):
            base = 8 + ((h >> 7) & 7)
            reg = 8 + ((h >> 2) & 7)
            offset = ((h >> 10) & 7) * 8 + ((h >> 6) & 1) * 4 + ((h >> 5) & 1) * 64
            result.append(('lw' if funct == 2 else 'sw', reg, base, offset))
        elif h & 3 == 1 and funct == 3:
            rd = (h >> 7) & 31
            imm = ((h >> 2) & 31) | (((h >> 12) & 1) << 5)
            check(rd not in (0, 2) and imm != 0, 'invalid c.lui')
            imm = imm - 64 if imm & 32 else imm
            result.append(('lui', rd, (imm << 12) & 0xffffffff))
        elif h & 0xfc63 == 0x8c41:
            result.append(('or', 8 + ((h >> 7) & 7), 8 + ((h >> 2) & 7)))
        else:
            raise ValueError('unsupported compressed opcode')
        pos += 2
    return result

def model90(write, value):
    write(0x4002200c, value)
    return value

def modelb6(read, write, value):
    word = read(0x40022010)
    write(0x40022010, word | 0x8000)
    return value

def main():
    image = BIN.read_bytes()
    check(len(image) == 76800, 'image length')
    check(digest(image) == '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667', 'image hash')
    check(digest((HERE / 'candidate.c').read_bytes()) == '212e26afc031097e43ea2a22f169f78d83c2d237353f4d43d4d920a2068ebeeb', 'C hash')
    windows = [(0x18e90, 0x18e98, '4937a9406887122dfa589dbe9fee75572e5cccd9ae20f52e7f9a59e140e2c466', [('lui',15,0x40022000),('sw',10,15,12),('ret',)]),
               (0x18eb6, 0x18ec4, '20c1f57d6f8294aa24230996a9311f4a73ae3da72b0eed0acc4da3e2330ea7de', [('lui',14,0x40022000),('lw',15,14,16),('lui',13,0x8000),('or',15,13),('sw',15,14,16),('ret',)])]
    for start, end, pin, expected in windows:
        data = image[start - 0x8000:end - 0x8000]
        check(len(data) == end - start and digest(data) == pin, 'window pin')
        check(decode(data) == expected, 'decoded instructions')
    for bad in (b'\x03\x00', b'\x00\x00', b'\x01'):
        try:
            decode(bad)
        except ValueError:
            pass
        else:
            raise ValueError('negative decode accepted')
    events = []
    def read(addr):
        events.append(('read', addr))
        return len(events)  # distinct fresh reads
    def write(addr, val):
        events.append(('write', addr, val))
    check(model90(write, 0x40022010) == 0x40022010, '90 return')
    check(modelb6(read, write, 0x8000) == 0x8000, 'b6 return')
    check(modelb6(read, write, 0x40022010) == 0x40022010, 'alias return')
    check(events == [('write',0x4002200c,0x40022010),('read',0x40022010),('write',0x40022010,0x8002),('read',0x40022010),('write',0x40022010,0x8004)], 'event order')
    print('OK: static decode and Python abstract events; C untested')

if __name__ == '__main__':
    main()
