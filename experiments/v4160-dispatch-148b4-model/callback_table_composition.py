"""Compose bounded 0x90b0 scan and match projections over synthetic tables.

Projection boundaries reconstruct memory, not a single machine state. No real
providers execute; memory and caller-saved assumptions are as in both modules.
"""
import hashlib
import importlib.util
import random
from pathlib import Path


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().with_name(name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


match = load_module('callback_table_match')
scan = load_module('callback_table_scan')

IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'


def composed(image, key, keys, payloads, gp_byte):
    if len(keys) != 15 or len(payloads) != 15: raise ValueError('expected 15 entries')
    kind, index, reads, state = scan.run(image, key, keys)
    if kind == 'miss':
        if (index, state) != (1, (0x20002000, 0x22222222, 0x33333333)):
            raise ValueError('miss frame mismatch')
        return kind, reads, [], [], None
    if kind != 'match' or state != (0x20001ff0, scan.BASE, key):
        raise ValueError('scan-to-continuation frame mismatch')
    table = {scan.BASE + 12 * i + offset: value
             for i in range(15) for offset, value in ((4, keys[i]), (8, payloads[i]))}
    calls, writes, regs, memory = match.run(image, index, payloads[index], gp_byte, table)
    expected = dict(table)
    expected[scan.BASE + 12 * index + 4] = 0
    expected[scan.BASE + 12 * index + 8] = 0
    if memory != expected: raise ValueError('continuation table preservation mismatch')
    return kind, reads, calls, writes, regs


def verify_case(image, key, keys, payloads, gp_byte):
    kind, reads, calls, writes, regs = composed(image, key, keys, payloads, gp_byte)
    found = next((i for i, value in enumerate(keys) if value == key), None)
    limit = 15 if found is None else found + 1
    if reads != [scan.BASE + 12 * i + 4 for i in range(limit)]: raise ValueError('scan order mismatch')
    if found is None:
        if (kind, calls, writes, regs) != ('miss', [], [], None): raise ValueError('miss changed state')
        return
    entry = scan.BASE + 12 * found
    expected_calls = [] if payloads[found] == 0 else [(0x13572468, payloads[found])]
    expected_regs = (gp_byte, 1 << found, 0x14800, 0x20002000, 0x22222222, 0x33333333)
    if (kind, calls, writes, regs) != ('match', expected_calls, [(entry + 4, 0), (entry + 8, 0)], expected_regs):
        raise ValueError('match effects mismatch')


def main():
    image = IMAGE.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != SHA: raise ValueError('firmware identity mismatch')
    for index in range(15):
        for payload in (0, 0xffffffff):
            keys, payloads = [0] * 15, [0] * 15
            keys[index], payloads[index], keys[-1] = 7, payload, 7
            verify_case(image, 7, keys, payloads, 255)
    verify_case(image, 8, [0]*15, [0xffffffff]*15, 0)
    rng = random.Random(0xc011bac0)
    for _ in range(4096):
        keys = [rng.randrange(8) for _ in range(15)]
        payloads = [rng.choice((0, rng.getrandbits(32))) for _ in range(15)]
        verify_case(image, rng.randrange(10), keys, payloads, rng.randrange(256))
    for address in (0x90c8, 0x90fe):
        mutant = bytearray(image)
        mutant[address - 0x8000] ^= 4
        try: verify_case(mutant, 7, [7]*15, [1]*15, 2)
        except ValueError: pass
        else: raise ValueError(f'composition mutation missed at {address:#x}')
    print('PASS: 4127 composed synthetic table cases, duplicate priority, misses and both mutations; provider bodies excluded')


if __name__ == '__main__': main()
