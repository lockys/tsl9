"""Compare a portable C entry projection with original-byte execution."""
import argparse
import ctypes
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('entry_verify', HERE / 'verify.py')
verification = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verification)
BIN, SHA, CODE, BASE, run = (verification.BIN, verification.SHA, verification.CODE,
                              verification.BASE, verification.run)


def worker(dll):
    image = BIN.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != SHA: raise ValueError('firmware identity mismatch')
    code = image[BASE-0x8000:BASE-0x8000+len(CODE)]
    if code != CODE: raise ValueError('entry window mismatch')
    lib = ctypes.CDLL(str(dll))
    word = ctypes.c_uint32
    fn = lib.event_entry_projection
    fn.argtypes = [word, word, word, word, ctypes.POINTER(word)]
    fn.restype = None
    count = 0
    for post in range(65536):
        for result, sp in ((0, 0x20001000), (0xffffffff, 0x10)):
            ra = (0x12340000 | post)
            pc, x, saved, calls, reads = run(code, post ^ 1, post, result, sp, ra)
            out = (word * 9)()
            fn(post, result, sp, ra, out)
            expected = [pc, x[10], x[13], x[14], x[15], x[2], (sp-4)&0xffffffff, saved[(sp-4)&0xffffffff], calls[0][0]]
            if list(out) != expected or calls[0][1] != 0 or reads != [0x2000c796]:
                raise ValueError(f'entry mismatch post={post:#x}')
            count += 1
    # Additional RV32 wrap boundaries, independently of alignment/hardware.
    for sp in (0, 1, 4, 15, 16, 0xffffffff):
        pc, x, saved, calls, reads = run(code, 0, 0xfffe, 5, sp, 0x12345678)
        out = (word * 9)()
        fn(0xfffe, 5, sp, 0x12345678, out)
        if list(out) != [pc, x[10], x[13], x[14], x[15], x[2], (sp-4)&0xffffffff, saved[(sp-4)&0xffffffff], calls[0][0]]:
            raise ValueError(f'entry mismatch sp={sp:#x}')
    print(f'PASS: {count} cases and 6 RV32 stack arithmetic boundaries', flush=True)


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars', type=Path)
    group.add_argument('--worker', type=Path)
    args = parser.parse_args()
    if args.worker:
        worker(args.worker)
        return
    with tempfile.TemporaryDirectory(prefix='tsl9-event-entry-') as tmp:
        tmp = Path(tmp)
        batch = tmp / 'build.bat'
        def compile_one(source, dll, flags):
            batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{source}" /Fe:"{dll}"\n@exit /b %errorlevel%\n', encoding='utf-8')
            subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=tmp, check=True)
        for name, flags in (('C', '/TC /std:c11'), ('C++', '/TP /std:c++17')):
            dll = tmp / (name.replace('+', 'p')+'.dll')
            compile_one(HERE / 'model.c', dll, flags)
            print(name + ': ', end='', flush=True)
            subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--worker', str(dll)], check=True)
        text = (HERE / 'model.c').read_text(encoding='utf-8')
        for name, before, after in (('branch', 'post_half == UINT32_C(0xfffe)', 'post_half != UINT32_C(0xfffe)'), ('address', 'UINT32_C(0x2000c794)', 'UINT32_C(0x2000c796)')):
            if text.count(before) != 1: raise ValueError('ambiguous mutant')
            source, dll = tmp / (name+'.c'), tmp / (name+'.dll')
            source.write_text(text.replace(before, after), encoding='utf-8')
            compile_one(source, dll, '/TC /std:c11')
            check = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--worker', str(dll)], capture_output=True, text=True)
            if check.returncode == 0 or 'entry mismatch' not in check.stderr: raise ValueError(f'{name} mutant not detected')
            print(f'PASS: {name} mutant rejected')
    print('Returning callee stub, successful synthetic loads; no hardware or physical stack access.')


if __name__ == '__main__': main()
