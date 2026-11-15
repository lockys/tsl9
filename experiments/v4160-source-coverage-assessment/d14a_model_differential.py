#!/usr/bin/env python3
"""Compare C/C++ host models against the pinned offline instruction decoder."""
import argparse
import ctypes
import hashlib
import importlib.util
from pathlib import Path
import random
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('d14a_projection', ROOT / 'd14a-offline-projection.py')
projection = importlib.util.module_from_spec(spec)
spec.loader.exec_module(projection)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def run(dll):
    lib = ctypes.CDLL(str(dll))
    read_type = ctypes.CFUNCTYPE(ctypes.c_uint8, ctypes.c_void_p, ctypes.c_uint32)
    write_type = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint8)
    fn = lib.d14a_model
    fn.argtypes = [ctypes.c_void_p, read_type, write_type, ctypes.c_uint32, ctypes.c_uint32]
    fn.restype = ctypes.c_uint32
    rng = random.Random(0xd14a)
    for i in range(4096):
        gp = (0xffffff70, 0, 0x20004000, rng.getrandbits(32))[i % 4]
        p = (gp + 232 + (i % 25) - 12) & projection.MASK
        addresses = {(p+k) & projection.MASK for k in (3, 5, 7, 9)} | {(gp+k) & projection.MASK for k in range(232, 236)}
        memory = {a: rng.randrange(256) for a in sorted(addresses)}
        if i % 2 == 0:
            for s, d in zip((3, 5, 7, 9), range(232, 236)):
                memory[(gp+d) & projection.MASK] = memory[(p+s) & projection.MASK]
        if i < 5:
            gp, p = 0x20004000, 0x20005000
            values = (10, 20, 30, 40)
            memory = {p+offset: value for offset, value in zip((3, 5, 7, 9), values)}
            memory.update({gp+232+j: value ^ (1 if i == j else 0) for j, value in enumerate(values)})
        expected = projection.run(projection.CODE, p, gp, memory)
        actual_memory = dict(memory)
        trace = []
        @read_type
        def read_byte(_ctx, address):
            value = actual_memory[address]
            trace.append(('read', address, value))
            return value
        @write_type
        def write_byte(_ctx, address, value):
            actual_memory[address] = value
            trace.append(('write', address, value))
        target = fn(None, read_byte, write_byte, p, gp)
        expected_target = 0 if expected[0] == 'return' else expected[0]
        need((target, actual_memory, trace) == (expected_target, expected[1], expected[2]), 'case '+str(i))
    print('PASS: 4096 C model vs instruction-decoder shared-memory traces', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ('clang', 'linker', 'image', 'worker'):
        parser.add_argument('--'+option, type=Path)
    args = parser.parse_args()
    if args.worker:
        run(args.worker)
        return
    if any(x is None for x in (args.clang, args.linker, args.image)):
        parser.error('--clang, --linker and --image are required')
    image = args.image.read_bytes()
    need(hashlib.sha256(image).hexdigest() == projection.SHA256, 'image hash')
    need(image[projection.PC-projection.BASE:projection.END-projection.BASE] == projection.CODE, 'image instructions')
    with tempfile.TemporaryDirectory(prefix='tsl9-d14a-model-') as tmp:
        root = Path(tmp)
        # Use distinct DLL paths: Windows retains a loaded library in-process.
        for language, standard in (('c', 'c11'), ('c++', 'c++17')):
            obj, dll = root / (standard+'.obj'), root / (standard+'.dll')
            subprocess.run([str(args.clang), '--target=x86_64-pc-windows-msvc', '-c', '-x', language,
                            '-std='+standard, str(ROOT/'d14a_model.c'), '-o', str(obj)], check=True)
            subprocess.run([str(args.linker), '/nologo', '/dll', '/noentry', '/nodefaultlib',
                            str(obj), '/out:'+str(dll)], check=True)
            optimize = ['-' + 'O' * sys.flags.optimize] if sys.flags.optimize else []
            subprocess.run([sys.executable, *optimize, str(Path(__file__).resolve()), '--worker', str(dll)], check=True)
            print('PASS:', standard, flush=True)
    print('LIMIT: successful accesses and stable synthetic RAM; no target ABI, terminal registers, downstream or hardware')


if __name__ == '__main__':
    main()
