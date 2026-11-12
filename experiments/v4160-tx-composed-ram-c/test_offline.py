"""BIN/source pins and independent Python illustrations; does not test C."""
from pathlib import Path
from hashlib import sha256

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BIN = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
HEADER = bytes.fromhex('93076042 b307f602 97260020 9386666b 6177 134757f5 9375f40f 9907 b697 2390e700 2382b700 13578400 ce95 a381e700 2e97 23813701 1377f70f 8145')
LOOP = bytes.fromhex('13950501418163618504a297a382e70093076042b307f60219040a06f240d2444249b2498545b6972391870023920700938741093e966244b707040003a3070503450600056102833385b400034505003388b70085052a97a302a8001377f70f45b7')
PIN = 'de88c0b5677d5d036443e022c6ac71b41e7b7de347c184908cc9fc1039d957cf'
B = 0x2000b18c


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(header, loop, source):
    require(header == HEADER and loop == LOOP, 'BIN window mismatch')
    require(sha256(source).hexdigest() == PIN, 'source mismatch')


def example(mem, base, source, bank, length, command, a6):
    d = base + 1062 * bank + 6
    address = B + 1062 * bank + 6
    events = []
    def store(index, value):
        mem[index] = value
        events.append(('w', index, value))
    store(d, 0x55)
    store(d + 1, 0x7f)
    store(d + 4, length & 255)
    store(d + 3, (length >> 8) & 255)
    store(d + 2, command & 255)
    checksum = ((length >> 8) + (length & 255) + command) & 255
    i = 0
    while (i & 65535) < length:
        require(i < length and i < 65535, 'iteration bound')
        value = mem[source + i]
        events.append(('r', source + i, value))
        a6 = address + i
        store(d + i + 5, value)
        checksum = (checksum + value) & 255
        i += 1
    return (i & 65535, i, bank, B, checksum, address, a6), events


def run():
    with BIN.open('rb') as f:
        f.seek(0x8ace - 0x8000)
        header = f.read(len(HEADER))
        f.seek(0x8b0a - 0x8000)
        loop = f.read(len(LOOP))
    source = (HERE / 'candidate.c').read_bytes()
    validate(header, loop, source)
    for which, window in enumerate((header, loop)):
        for i in range(len(window)):
            changed = bytearray(window)
            changed[i] ^= 1
            try:
                validate(bytes(changed) if which == 0 else header,
                         bytes(changed) if which == 1 else loop, source)
            except ValueError:
                continue
            raise ValueError('BIN mutation accepted')
    try:
        validate(header, loop, source + b' ')
    except ValueError:
        pass
    else:
        raise ValueError('source mutation accepted')
    m = bytearray(64)
    m[30:33] = bytes([1, 2, 3])
    regs, ev = example(m, 0, 30, 0, 3, 0x102, 0xdeadbeef)
    require(regs == (3, 3, 0, B, 11, B+6, B+8), 'non-alias registers')
    require(ev == [('w',6,85),('w',7,127),('w',10,3),('w',9,0),('w',8,2),('r',30,1),('w',11,1),('r',31,2),('w',12,2),('r',32,3),('w',13,3)], 'non-alias events')
    m = bytearray([0xaa] * 64)
    regs, ev = example(m, 0, 10, 0, 3, 4, 9)
    require(regs == (3, 3, 0, B, 16, B+6, B+8), 'alias registers')
    require(ev[5:] == [('r',10,3),('w',11,3),('r',11,3),('w',12,3),('r',12,3),('w',13,3)], 'alias propagation')
    require(m[14] == 0xaa, 'tail touched')
    m = bytearray(1200)
    regs, ev = example(m, 0, 0, 1, 0, 0xffffffff, 0xabcdef01)
    require(regs == (0, 0, 1, B, 255, B+1068, 0xabcdef01) and len(ev) == 5, 'zero edge')
    m = bytearray(131100)
    m[65550:65550+65535] = bytes((i % 251) + 1 for i in range(65535))
    m[65546] = 0xa5  # One byte immediately after the destination range.
    regs, ev = example(m, 0, 65550, 0, 65535, 0, 9)
    require(regs == (65535, 65535, 0, B, 220, B+6, B+6+65534), 'exact upper edge')
    require(len(ev) == 5 + 2*65535 and m[65545] == 24 and m[65546] == 0xa5, 'upper bound')
    print('BIN/source pins, negative mutations and Python examples passed; C was not tested.')


if __name__ == '__main__':
    run()
