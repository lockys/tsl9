"""Compare C/C++ event tail projection against bounded instruction execution."""
import argparse
import ctypes
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('event_tail', HERE / 'tail.py')
tail = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tail)


def worker(dll):
    image = tail.BIN.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != tail.SHA: raise ValueError('firmware identity mismatch')
    lib = ctypes.CDLL(str(dll))
    word = ctypes.c_uint32
    fn = lib.event_tail_projection
    fn.argtypes = [word]*6 + [ctypes.POINTER(word)]
    fn.restype = None
    out = (word * 14)()
    count = 0
    for previous in (0, 0x10, 0xffffffef, 0xffffffff):
        for delta in list(range(65536)) + [0x7fffffff, 0x80000000, 0xffffffff]:
            clock = (previous + delta) & 0xffffffff
            for result in (0, 1, 0xffffffff):
                gp, sp, ra = 0xfffffff0, 0x20001000, 0x12345678
                pc, args, restored_sp, restored_ra, reads, writes, calls = tail.run(image, result, clock, previous, gp, sp, ra)
                fn(result, clock, previous, gp, sp, ra, out)
                padded = list(args) + [0] * (4-len(args))
                expected = [pc, *padded, restored_sp, restored_ra,
                            len(reads), reads[0] if reads else 0,
                            len(writes), writes[0][0] if writes else 0,
                            writes[0][1] if writes else 0,
                            len(calls), calls[0] if calls else 0]
                if list(out) != expected:
                    raise ValueError(f'tail model mismatch prev={previous:#x} delta={delta:#x} result={result:#x}')
                count += 1
    print(f'PASS: {count} C model vs bounded-instruction traces', flush=True)


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars', type=Path)
    group.add_argument('--worker', type=Path)
    args = parser.parse_args()
    if args.worker:
        worker(args.worker)
        return
    with tempfile.TemporaryDirectory(prefix='tsl9-event-tail-') as temp:
        tmp = Path(temp)
        batch = tmp / 'build.bat'
        def compile_one(source, dll, flags):
            batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{source}" /Fe:"{dll}"\n@exit /b %errorlevel%\n', encoding='utf-8')
            subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=tmp, check=True)
        for name, flags in (('C', '/TC /std:c11'), ('C++', '/TP /std:c++17')):
            dll = tmp / (name.replace('+','p') + '.dll')
            compile_one(HERE/'tail_model.c', dll, flags)
            print(name + ': ', end='', flush=True)
            subprocess.run([sys.executable, '-I', '-B', str(Path(__file__).resolve()), '--worker', str(dll)], check=True)
        text = (HERE/'tail_model.c').read_text(encoding='utf-8')
        mutants = (('threshold', 'UINT32_C(34)', 'UINT32_C(35)'),
                   ('reverse_subtract', 'clock - previous', 'previous - clock'),
                   ('nonzero_delay', 'out[3] = 100;', 'out[3] = 99;'),
                   ('no_update', 'out[9] = 1;', 'out[9] = 0;'))
        for name, old, new in mutants:
            if text.count(old) != 1: raise ValueError('ambiguous mutation')
            source, dll = tmp/(name+'.c'), tmp/(name+'.dll')
            source.write_text(text.replace(old, new), encoding='utf-8')
            compile_one(source, dll, '/TC /std:c11')
            check = subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)], capture_output=True, text=True)
            if check.returncode == 0 or 'tail model mismatch' not in check.stderr: raise ValueError(f'{name} mutant not rejected')
            print(f'PASS: {name} mutant rejected', flush=True)
    print('Returning clock stub and synthetic reads; no tail target or hardware execution.')


if __name__ == '__main__': main()
