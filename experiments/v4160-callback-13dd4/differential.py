"""Compare callback C projection with bounded original-byte execution."""
import argparse
import ctypes
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
from verify import BIN, SHA, BASE, CODE
from wrapper import run

HERE = Path(__file__).resolve().parent


def worker(dll):
    image = BIN.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != SHA: raise ValueError('firmware identity mismatch')
    code = image[BASE-0x8000:BASE-0x8000+len(CODE)]
    if code != CODE: raise ValueError('callback bytes mismatch')
    library = ctypes.CDLL(str(dll))
    word = ctypes.c_uint32
    fn = library.callback_projection
    fn.argtypes = [word, word, ctypes.POINTER(word)]
    fn.restype = None
    count = 0
    for queue in range(256):
        for sp in (0, 0x20001000, 0xfffffff0):
            for first in (0, 0xffffffff):
                for second in (0, 0x87654321):
                    kind, final_sp, calls = run(code, queue, 0x10000101, sp, first, second)
                    out = (word * 12)()
                    fn(queue, sp, out)
                    expected = [int(kind == 'tail'), final_sp, *[c[0] for c in calls[:3]],
                                calls[0][1][0], calls[1][1][0]]
                    expected += list(calls[3][1]) + [calls[3][0]] if kind == 'tail' else [0]*5
                    if list(out) != expected: raise ValueError(f'callback mismatch: queue={queue} sp={sp:#x}')
                    count += 1
    print(f'PASS: {count} C model vs original-byte wrapper traces', flush=True)


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars', type=Path)
    group.add_argument('--worker', type=Path)
    args = parser.parse_args()
    if args.worker:
        worker(args.worker)
        return
    with tempfile.TemporaryDirectory(prefix='tsl9-callback-model-') as tmp:
        batch = Path(tmp) / 'build.bat'
        for name, flags in (('C', '/TC /std:c11'), ('C++', '/TP /std:c++17')):
            dll = Path(tmp) / (name.replace('+', 'p') + '.dll')
            batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{HERE / "model.c"}" /Fe:"{dll}"\n@exit /b %errorlevel%\n', encoding='utf-8')
            subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=tmp, check=True)
            print(name + ': ', end='', flush=True)
            subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--worker', str(dll)], check=True)
        source = (HERE / 'model.c').read_text(encoding='utf-8')
        for name, before, after in (('inverted', 'queue_status == 0', 'queue_status != 0'),
                                    ('delay', 'out[9] = 300;', 'out[9] = 301;')):
            if source.count(before) != 1: raise ValueError('ambiguous mutant')
            mutant, dll = Path(tmp) / (name+'.c'), Path(tmp) / (name+'.dll')
            mutant.write_text(source.replace(before, after), encoding='utf-8')
            batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD /TC /std:c11 "{mutant}" /Fe:"{dll}"\n@exit /b %errorlevel%\n', encoding='utf-8')
            subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=tmp, check=True)
            result = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--worker', str(dll)], capture_output=True, text=True)
            if result.returncode == 0 or 'callback mismatch:' not in result.stderr: raise ValueError(f'{name} mutant not detected')
            print(f'PASS: {name} semantic mutant rejected')
    print('Synthetic returning stubs only; no physical execution or external side effects.')


if __name__ == '__main__': main()
