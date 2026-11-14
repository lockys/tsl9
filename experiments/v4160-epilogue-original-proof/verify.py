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


def check(actual, original, start, end, expected_range=(START, END)):
    if (start, end) != expected_range or len(actual) != end - start:
        raise ValueError('wrong ownership interval or section size')
    if actual != original[start - BASE:end - BASE]:
        raise ValueError('fragment differs from original BIN')


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
    tools = runpy.run_path(str(ROOT / 'scripts/source-ota-epilogue.py'))
    compile_fragment = tools['compile_fragment']
    compile_entry = tools['compile_entry']
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
            entry_start, entry_end = 0x14056, START
            entry = compile_entry(args.tool_dir, Path(tmp), mode, elf)
            check(entry, original, entry_start, entry_end, (entry_start, entry_end))
            for i in range(len(entry)):
                mutant = bytearray(entry)
                mutant[i] ^= 1
                try:
                    check(mutant, original, entry_start, entry_end, (entry_start, entry_end))
                except ValueError:
                    continue
                raise RuntimeError(f'{mode}: entry mutant {i} accepted')
            for start, end in ((entry_start-1, entry_end), (entry_start+1, entry_end), (entry_start, entry_end-1), (entry_start, entry_end+1)):
                try:
                    check(entry, original, start, end, (entry_start, entry_end))
                except ValueError:
                    continue
                raise RuntimeError(f'{mode}: wrong entry boundary accepted')
            print(f'PASS {mode}: 66 linked entry bytes equal pinned BIN; relocation layout, 66 mutations and 4 boundaries checked')
            fragments = (('compile_more', 0x140a6, 0x140dc),
                         ('compile_ae', 0x140dc, 0x14122),
                         ('compile_ad', 0x1417a, 0x141ac))
            for name, fragment_start, fragment_end in fragments:
                fragment = tools[name](args.tool_dir, Path(tmp), mode, elf)
                interval = (fragment_start, fragment_end)
                check(fragment, original, *interval, interval)
                for i in range(len(fragment)):
                    mutant = bytearray(fragment)
                    mutant[i] ^= 1
                    try:
                        check(mutant, original, *interval, interval)
                    except ValueError:
                        continue
                    raise RuntimeError(f'{mode}: {name} mutant {i} accepted')
                for start, end in ((fragment_start - 1, fragment_end),
                                   (fragment_start + 1, fragment_end),
                                   (fragment_start, fragment_end - 1),
                                   (fragment_start, fragment_end + 1)):
                    try:
                        check(fragment, original, start, end, interval)
                    except ValueError:
                        continue
                    raise RuntimeError(f'{mode}: {name} wrong boundary accepted')
                print(f'PASS {mode}: {name} [{fragment_start:#x},{fragment_end:#x}) matches original; {len(fragment)} byte mutations and 4 boundaries rejected')
    print('Bounded check only: no coverage-policy change, complete image, execution or hardware claim.')


if __name__ == '__main__':
    main()
