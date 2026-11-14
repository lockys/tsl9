"""Compare host C/C++ semantic projection to bounded original-byte execution."""
import argparse
import ctypes
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
from verify import BIN, SHA, run

HERE = Path(__file__).resolve().parent


def worker(path):
    image = BIN.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != SHA:
        raise ValueError('firmware identity mismatch')
    library = ctypes.CDLL(str(path))
    word = ctypes.c_uint32
    fn = library.record_update_a1_one
    fn.argtypes = [word, ctypes.c_uint16, ctypes.c_uint16, ctypes.POINTER(word)]
    fn.restype = None
    count = 0
    for value in list(range(0, 65536, 8)) + [0xffff, 0xfffe, 0x8000, 0x7fff]:
        for handle, first, second in ((value, value, value ^ 1), (value, value ^ 1, value),
                                      (value, value, value), (value, value ^ 1, value ^ 1),
                                      (value | 0x10000, value, value)):
            reads, writes, regs = run(image, handle, first, second, state=True)
            if (regs[1], regs[2], regs[10], regs[11]) != (0x12345678, 0x20001000, handle, 1):
                raise ValueError('ra/sp/a0/a1 changed')
            if any(regs[reg] != 0xa5000000 | reg for reg in (8, 9, *range(18, 28))):
                raise ValueError('callee-saved register changed')
            actual = (word * 8)()
            fn(handle, first, second, actual)
            expected = [len(reads)] + reads + [0] * (2-len(reads)) + [len(writes)]
            expected += [item for event in writes for item in event]
            expected += [0] * (8-len(expected))
            if list(actual) != expected:
                raise ValueError(f'mismatch: {handle:#x}, {first:#x}, {second:#x}')
            count += 1
    print(f'PASS: {count} C model vs original-byte interpreter cases, ordered reads/writes and preserved registers', flush=True)
    other = library.record_update_other
    other.argtypes = [word, word, ctypes.c_uint16, ctypes.c_uint16, ctypes.POINTER(word)]
    other.restype = None
    count = 0
    for value in list(range(0, 65536, 8)) + [0xffff, 0xfffe, 0x8000, 0x7fff]:
        for mode in (0, 3, 0xffffffff):
            for handle, first, second in ((value, value, value ^ 1), (value, value ^ 1, value),
                                          (value, value, value), (value, value ^ 1, value ^ 1),
                                          (value | 0x10000, value, value)):
                compare_other(image, other, handle, mode, first, second)
                count += 1
        for handle, first, second in ((value, 0xfffe, value), (value | 0x10000, 0xfffe, 0xfffe),
                                      (value, 0xffff, 0xfffe), (value, 0xffff, 0xffff)):
            compare_other(image, other, handle, 2, first, second)
            count += 1
    print(f'PASS: {count} other-mode C vs instruction decoder cases, ordered events and widths', flush=True)


def compare_other(image, fn, handle, mode, first, second):
    reads, writes = run(image, handle, first, second, mode=mode, detailed=True)
    output = (ctypes.c_uint32 * 13)()
    fn(handle, mode, first, second, output)
    expected = [len(reads)] + reads + [0] * (2 - len(reads)) + [len(writes)]
    for address, width, value in writes:
        expected.extend((address, width, value))
    expected += [0] * (13-len(expected))
    if list(output) != expected:
        raise ValueError(f'other-mode mismatch: {mode:#x}, {handle:#x}, {first:#x}, {second:#x}')


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars', type=Path)
    group.add_argument('--worker', type=Path)
    args = parser.parse_args()
    if args.worker:
        worker(args.worker)
        return
    with tempfile.TemporaryDirectory(prefix='tsl9-record-model-') as temp:
        for lang, flags in (('C', '/TC /std:c11'), ('C++', '/TP /std:c++17')):
            dll = Path(temp) / ('record-' + lang.replace('+', 'p') + '.dll')
            batch = Path(temp) / 'build.bat'
            batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{HERE / "model.c"}" /Fe:"{dll}"\n@exit /b %errorlevel%\n', encoding='utf-8')
            subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=temp, check=True)
            print(lang + ': ', end='', flush=True)
            # The child owns the DLL and releases it at process exit, including
            # failures, before TemporaryDirectory removes the build artifacts.
            subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--worker', str(dll)], check=True)
        source = (HERE / 'model.c').read_text(encoding='utf-8')
        mutations = (
            ('mode1-value', 'out[5] = 1;', 'out[5] = 0;', 'mismatch:'),
            ('sentinel', 'first == UINT16_C(0xfffe)', 'first == UINT16_C(0xfffd)', 'other-mode mismatch:'),
            ('store-width', 'out[5] = 2;', 'out[5] = 1;', 'other-mode mismatch:'),
        )
        for name, before, after, marker in mutations:
            if source.count(before) != 1: raise ValueError(f'ambiguous mutation: {name}')
            mutant = Path(temp) / (name + '.c')
            mutant.write_text(source.replace(before, after), encoding='utf-8')
            dll = Path(temp) / (name + '.dll')
            batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD /TC /std:c11 "{mutant}" /Fe:"{dll}"\n@exit /b %errorlevel%\n', encoding='utf-8')
            subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=temp, check=True)
            result = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--worker', str(dll)],
                                    capture_output=True, text=True)
            if result.returncode == 0 or marker not in result.stderr:
                raise ValueError(f'mutant {name} not rejected for intended mismatch: {result.stderr}')
            print(f'PASS: semantic mutant {name} rejected', flush=True)
    print('Synthetic successful accesses only; no physical execution or concurrent changes.')


if __name__ == '__main__': main()
