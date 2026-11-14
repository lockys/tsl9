"""Compare the C projection with independently decoded bounded byte projections."""
import ctypes
import hashlib
import importlib.util
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
IMAGE = HERE.parents[1] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    scan, match = load('callback_table_scan'), load('callback_table_match')
    data = IMAGE.read_bytes()
    if len(data) != 76800 or hashlib.sha256(data).hexdigest() != SHA: raise ValueError('firmware identity mismatch')
    dll = ctypes.CDLL(sys.argv[1])
    word = ctypes.c_uint32
    ptr = ctypes.POINTER(word)
    dll.callback_table_model.argtypes = [word, ptr, ptr, word, ptr]
    dll.callback_table_model.restype = None
    rng = random.Random(0xca11bac0)
    for case in range(5000):
        keys = [rng.randrange(24) for _ in range(15)]
        values = [rng.choice((0, rng.getrandbits(32))) for _ in range(15)]
        key, gp = rng.randrange(28), rng.randrange(256)
        ck, cv, out = (word * 15)(*keys), (word * 15)(*values), (word * 7)()
        dll.callback_table_model(key, ck, cv, gp, out)
        kind, index, _, _ = scan.run(data, key, keys)
        expected_keys, expected_values = keys[:], values[:]
        if kind == 'miss':
            expected = [0, 0, 0, 0, 0, 0, 1]
        else:
            calls, writes, regs, _ = match.run(data, index, values[index], gp)
            if writes != [(scan.BASE + 12*index + 4, 0), (scan.BASE + 12*index + 8, 0)]: raise ValueError('machine writes mismatch')
            expected = [1, index, int(bool(calls)), values[index], regs[0], regs[1], 0]
            expected_keys[index] = expected_values[index] = 0
        if list(out) != expected or list(ck) != expected_keys or list(cv) != expected_values:
            raise ValueError(f'case {case}: C model differs from byte projections')
    print('PASS: 5000 C model vs byte-projection table cases, full arrays and outputs')


if __name__ == '__main__': main()
