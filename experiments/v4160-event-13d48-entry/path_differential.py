"""Compare C/C++ short-circuit projection against pinned instruction paths."""
import argparse
import ctypes
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('event_paths', HERE / 'paths.py')
paths = importlib.util.module_from_spec(spec)
spec.loader.exec_module(paths)


def worker(dll):
    image = paths.BIN.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != paths.SHA: raise ValueError('firmware identity mismatch')
    lib = ctypes.CDLL(str(dll))
    word = ctypes.c_uint32
    fn = lib.event_paths_projection
    fn.argtypes = [word]*7 + [ctypes.POINTER(word)]
    fn.restype = None
    out = (word * 9)()
    count = 0
    for h0 in (0xfffe, 0x1234):
        for m0 in range(256):
            for h1 in (0xfffe, 0x1234):
                for m1 in range(256):
                    for result in (0, 1):
                        sp = (m0 * 4) & 0xffffffff
                        ra = 0xabcdef00 | m1
                        pc, a0, actual_sp, actual_ra, reads = paths.run(image, h0, m0, h1, m1, result, sp, ra)
                        fn(h0, m0, h1, m1, result, sp, ra, out)
                        expected = [pc, a0, actual_sp, actual_ra, len(reads), *reads] + [0]*(4-len(reads))
                        if list(out) != expected: raise ValueError(f'path model mismatch h0={h0:x} m0={m0} h1={h1:x} m1={m1} result={result}')
                        count += 1
    halfword_cases = 0
    for value in range(65536):
        for result in (0, 1):
            for h0, h1 in ((value, 0x1234), (0xfffe, value)):
                pc, a0, sp, ra, reads = paths.run(image, h0, 1, h1, 0, result, 0x20001000, 0xabcdef00)
                fn(h0, 1, h1, 0, result, 0x20001000, 0xabcdef00, out)
                expected = [pc, a0, sp, ra, len(reads), *reads] + [0]*(4-len(reads))
                if list(out) != expected: raise ValueError(f'path model mismatch halfword={value:#x}')
                halfword_cases += 1
    print(f'PASS: {count} byte-combination and {halfword_cases} exhaustive halfword C model traces', flush=True)


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars', type=Path)
    group.add_argument('--worker', type=Path)
    args = parser.parse_args()
    if args.worker:
        worker(args.worker)
        return
    with tempfile.TemporaryDirectory(prefix='tsl9-event-paths-') as temp:
        tmp = Path(temp)
        batch = tmp/'build.bat'
        def compile_one(source, dll, flags):
            batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{source}" /Fe:"{dll}"\n@exit /b %errorlevel%\n', encoding='utf-8')
            subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=tmp, check=True)
        for name, flags in (('C', '/TC /std:c11'), ('C++', '/TP /std:c++17')):
            dll = tmp/(name.replace('+','p')+'.dll')
            compile_one(HERE/'path_model.c', dll, flags)
            print(name+': ', end='', flush=True)
            subprocess.run([sys.executable, '-I', '-B', str(Path(__file__).resolve()), '--worker', str(dll)], check=True)
        text = (HERE/'path_model.c').read_text(encoding='utf-8')
        for name, old, new in (('first_sentinel', 'h0 != UINT32_C(0xfffe)', 'h0 == UINT32_C(0xfffe)'),
                               ('second_sentinel', 'h1 == UINT32_C(0xfffe)', 'h1 != UINT32_C(0xfffe)'),
                               ('last_byte', 'direct = m1 != 0;', 'direct = m1 == 0;')):
            if text.count(old) != 1: raise ValueError('ambiguous mutation')
            source, dll = tmp/(name+'.c'), tmp/(name+'.dll')
            source.write_text(text.replace(old,new), encoding='utf-8')
            compile_one(source, dll, '/TC /std:c11')
            check = subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)], capture_output=True, text=True)
            if check.returncode == 0 or 'path model mismatch' not in check.stderr: raise ValueError(f'{name} mutant not rejected')
            print(f'PASS: {name} mutant rejected', flush=True)
    print('No actual callee, hardware reads, concurrency or ABI clobber simulation.')


if __name__ == '__main__': main()
