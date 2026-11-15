#!/usr/bin/env python3
"""Test host compiler optimization separately from Python optimization."""
import argparse
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('d14a_projection', ROOT/'d14a-offline-projection.py')
projection = importlib.util.module_from_spec(spec)
spec.loader.exec_module(projection)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ('clang', 'linker', 'image'):
        parser.add_argument('--'+option, type=Path, required=True)
    args = parser.parse_args()
    image = args.image.read_bytes()
    if (hashlib.sha256(image).hexdigest() != projection.SHA256 or
            image[projection.PC-projection.BASE:projection.END-projection.BASE] != projection.CODE):
        raise ValueError('firmware identity or instruction bytes')
    with tempfile.TemporaryDirectory(prefix='tsl9-d14a-opt-') as tmp:
        root = Path(tmp)
        for language, standard in (('c', 'c11'), ('c++', 'c++17')):
            for opt in ('0', '2', 's'):
                obj, dll = root/'unit.obj', root/'unit.dll'
                subprocess.run([str(args.clang), '--target=x86_64-pc-windows-msvc', '-c', '-x', language,
                                '-std='+standard, '-O'+opt, str(ROOT/'d14a_model.c'), '-o', str(obj)], check=True)
                subprocess.run([str(args.linker), '/nologo', '/dll', '/noentry', '/nodefaultlib',
                                str(obj), '/out:'+str(dll)], check=True, capture_output=True)
                optimize = ['-' + 'O'*sys.flags.optimize] if sys.flags.optimize else []
                subprocess.run([sys.executable, *optimize, str(ROOT/'d14a_model_differential.py'),
                                '--worker', str(dll)], check=True)
                print('PASS:', standard, 'host -O'+opt, flush=True)
    print('LIMIT: synthetic stable RAM only; not target compiler, ABI, CPU or hardware')


if __name__ == '__main__':
    main()
