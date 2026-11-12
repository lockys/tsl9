"""Offline static pins and illustrative ordered events; never executes candidate C."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

def check(condition, message):
    if not condition:
        raise AssertionError(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

image = (ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
check(sha(image) == '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667', 'image pin')
window = bytes.fromhex('a297a382e70093076042b307f60219040a06f240d2444249b2498545b6972391870023920700938741093e966244b707040003a307050345060005610283')
def check_window(actual):
    check(actual == window, 'window pin')

check_window(image[0x8b14-0x8000:0x8b52-0x8000])
rows = json.loads((ROOT / 'analysis/transport-frame-2026-10-23/original-contract.json').read_text(encoding='utf-8'))['rows']
wanted = ['add a5, a5, s0', 'sb a4, 5(a5)', 'li a5, 1062', 'mul a5, a2, a5', 'addi s0, s0, 6', 'slli a2, a2, 0x2', 'lw ra, 28(sp)', 'lw s1, 20(sp)', 'lw s2, 16(sp)', 'lw s3, 12(sp)', 'li a1, 1', 'add a5, a5, a3', 'sh s0, 2(a5)', 'sh zero, 4(a5)', 'addi a5, gp, 148', 'add a2, a2, a5', 'lw s0, 24(sp)', 'lui a5, 0x40', 'lw t1, 80(a5)', 'lbu a0, 0(a2)', 'addi sp, sp, 32', 'jr t1']
selected = [r for r in rows if 0x8b14 <= r['addr'] < 0x8b52]
lengths = [2, 4, 4, 4, 2, 2, 2, 2, 2, 2, 2, 2, 4, 4, 4, 2, 2, 4, 4, 4, 2, 2]

def check_rows(items):
    check(len(items) == len(wanted) == len(lengths), 'row count')
    pos = 0
    for row, opcode, size in zip(items, wanted, lengths):
        check(row['addr'] == 0x8b14 + pos, 'row address')
        check(row['size'] == size, 'row size')
        check(row['opcode'] == opcode, 'operand/order pin')
        check(bytes.fromhex(row['bytes']) == window[pos:pos + size], 'row bytes/window')
        pos += size
    check(pos == len(window), 'row coverage')

check_rows(selected)
check(sha((HERE / 'candidate.c').read_bytes()) == '3c7e6aa8668125c0943130d8a404b1b4a1a56e0a4965723939781ea5a02f1a5a', 'source pin')

# Events are manually specified examples, not a C or ISA interpreter. Values of
# an SH are one event; no assertion about physical bus transactions is made.
def events(length, gp):
    m = 0xffffffff
    base, sp, bank, d = 0x2000b18c, 0x20002000, 0, 0x2000b192
    return [('sb', (d + length + 5) & m, 0x55),
            *[('lw', sp + off) for off in (28, 20, 16, 12)],
            ('sh', base + bank * 1062 + 2, (length + 6) & 0xffff),
            ('sh', base + bank * 1062 + 4, 0),
            ('lw', sp + 24), ('lw', 0x40050),
            ('lbu', (gp + 148 + 4 * bank) & m)]

zero = events(0, 0x40050 - 148)
wrap = events(0xffff, 0x2000b18e - 148)
check(zero[0] == ('sb', 0x2000b197, 0x55), 'zero checksum address')
check(zero[5][2] == 6 and zero[-1][1] == zero[-2][1] == 0x40050, 'tail-slot byte alias')
check(wrap[5] == ('sh', 0x2000b18e, 5) and wrap[-1][1] == wrap[5][1], '16-bit wrap/GP alias')
check(events(0xffffffff, 0)[0][1] == 0x2000b196, '32-bit address wrap')
# Mutations exercise the actual pin validators without changing the source files.
def rejects(fn, value):
    try:
        fn(value)
    except (AssertionError, ValueError, KeyError):
        return
    raise AssertionError('mutation accepted')

rejects(check_window, bytes([window[0] ^ 1]) + window[1:])
rejects(check_window, window[:-1])
for field, bad in (('addr', 0x8b17), ('size', 3), ('opcode', 'sh a4, 5(a5)'), ('bytes', 'a382e701')):
    changed = [dict(row) for row in selected]
    changed[1][field] = bad
    rejects(check_rows, changed)
print('PASS: image/window/rows/source pinned; ordered examples and validator negatives (Python only)')
