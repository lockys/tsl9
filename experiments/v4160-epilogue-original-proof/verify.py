"""Isolated original-BIN byte check; does not change official coverage policy."""
import argparse
import hashlib
from pathlib import Path
import runpy
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
START, END, BASE = 0x14098, 0x140a6, 0x8000
EXPECTED = bytes.fromhex('fa 50 6a 54 da 54 4a 59 ba 59 29 61 82 80')


def check(actual, original, start, end):
    if (start, end) != (START, END) or len(actual) != end - start:
        raise ValueError('wrong ownership interval or section size')
    if actual != original[start - BASE:end - BASE]:
        raise ValueError('epilogue differs from original BIN')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tool-dir', required=True, type=Path)
    args = parser.parse_args()
    original = BIN.read_bytes()
    if len(original) != 76800 or hashlib.sha256(original).hexdigest() != SHA:
        raise ValueError('firmware identity mismatch')
    if original[START-BASE:END-BASE] != EXPECTED:
        raise ValueError('unexpected pinned epilogue')
    elf = runpy.run_path(str(ROOT / 'src/native/tx_candidate/postpass/elf32.py'))['ELF']
    compile_fragment = runpy.run_path(str(ROOT / 'scripts/source-ota-epilogue.py'))['compile_fragment']
    with tempfile.TemporaryDirectory(prefix='tsl9-epilogue-proof-') as tmp:
        for mode in ('c', 'cpp'):
            compiled = compile_fragment(args.tool_dir, Path(tmp), mode, elf)
            check(compiled, original, START, END)
            for i in range(len(compiled)):
                mutant = bytearray(compiled)
                mutant[i] ^= 1
                try:
                    check(mutant, original, START, END)
                except ValueError:
                    continue
                raise RuntimeError(f'{mode}: mutant {i} accepted')
            for start, end in ((START-1, END), (START+1, END), (START, END-1), (START, END+1)):
                try:
                    check(compiled, original, start, end)
                except ValueError:
                    continue
                raise RuntimeError(f'{mode}: wrong boundary accepted')
            print(f'PASS {mode}: 14 bytes equal pinned BIN, section/symbol/no relocations checked; 14 mutations and 4 boundaries rejected')
    print('Bounded check only: no coverage-policy change, linked image, execution or hardware claim.')


if __name__ == '__main__':
    main()
