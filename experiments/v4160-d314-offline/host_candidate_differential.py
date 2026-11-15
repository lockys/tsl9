#!/usr/bin/env python3
"""Run the actual d314 C source on a host fixture, not on the firmware target."""
import argparse
import ctypes
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile


def need(ok, message):
    if not ok:
        raise ValueError(message)


def worker(dll, decoder_path, image, mutant):
    spec = importlib.util.spec_from_file_location('d314_decode', decoder_path)
    decoder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(decoder)
    raw = Path(image).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == decoder.verify.IMAGE_SHA256, 'image hash')
    decoder.decode(raw[decoder.PC-decoder.verify.IMAGE_BASE:decoder.PC-decoder.verify.IMAGE_BASE+14])
    lib = ctypes.CDLL(str(dll))
    setter, getter = lib.write_storage, lib.read_storage
    setter.argtypes, setter.restype = [ctypes.c_ushort], None
    getter.argtypes, getter.restype = [], ctypes.c_ushort
    fn = lib.read_candidate
    fn.argtypes, fn.restype = [], ctypes.c_uint
    if mutant:
        mismatches = []
        for value in (0, 1, 256, 65535):
            setter(value)
            need(getter() == value, 'fixture truncates mutant input')
            actual = fn()
            need(getter() == value, 'mutant changed fixture')
            if actual != decoder.project(value):
                mismatches.append(value)
        need(mismatches, 'mutant survived')
        print('mutant rejected for values:', mismatches)
        return
    for value in range(65536):
        setter(value)
        need(getter() == value, 'fixture failed to set value '+str(value))
        need(fn() == decoder.project(value), 'candidate mismatch at '+str(value))
        need(getter() == value, 'fixture final value changed at '+str(value))
    print('65536 candidate vs instruction projection cases passed')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--candidate', type=Path)
    p.add_argument('--decoder', type=Path)
    p.add_argument('--image', type=Path)
    p.add_argument('--clang', type=Path)
    p.add_argument('--linker', type=Path)
    p.add_argument('--worker', type=Path)
    p.add_argument('--mutant', action='store_true')
    a = p.parse_args()
    if a.worker:
        worker(a.worker, a.decoder, a.image, a.mutant)
        return
    if any(x is None for x in (a.candidate, a.decoder, a.image, a.clang, a.linker)):
        p.error('--candidate, --decoder, --image, --clang and --linker are required')
    a.candidate, a.decoder, a.image, a.clang, a.linker = (x.resolve() for x in (a.candidate, a.decoder, a.image, a.clang, a.linker))
    source = a.candidate.read_text(encoding='utf-8')
    anchor = 'return tsl9_d314_data != 0;'
    need(source.count(anchor) == 1, 'candidate anchor')
    variants = {'actual': source, 'inverted': source.replace(anchor, 'return tsl9_d314_data == 0;'),
                'constant': source.replace(anchor, 'return 0;'),
                'byte': source.replace(anchor, 'return (*(volatile unsigned char *)&tsl9_d314_data) != 0;')}
    need(len(set(variants.values())) == len(variants), 'candidate mutants')
    fixture = '''\n#ifdef __cplusplus\nextern "C" {\n#endif\nvolatile unsigned short tsl9_d314_data;\n__declspec(dllexport) void write_storage(unsigned short v) {tsl9_d314_data=v;}\n__declspec(dllexport) unsigned short read_storage(void) {return tsl9_d314_data;}\n__declspec(dllexport) unsigned int read_candidate(void) {return __tsl9v4160_call_d314();}\n#ifdef __cplusplus\n}\n#endif\n'''
    source_hash = hashlib.sha256(a.candidate.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix='tsl9-d314-host-') as tmp:
        root = Path(tmp)
        for lang, std in [('c', 'c11'), ('c++', 'c++17')]:
            for name, candidate in variants.items():
                unit, dll, bat = root/'unit.c', root/'unit.dll', root/'compile.bat'
                unit.write_text(candidate + fixture, encoding='utf-8')
                linker = a.linker
                obj = root/'unit.obj'
                bat.write_text(f'@"{a.clang}" --target=x86_64-pc-windows-msvc -c -x {lang} -std={std} "{unit}" -o "{obj}"\n@if errorlevel 1 exit /b 1\n@"{linker}" /nologo /dll /noentry /nodefaultlib "{obj}" /out:"{dll}"\n@exit /b %errorlevel%\n', encoding='utf-8')
                subprocess.run(['cmd.exe', '/d', '/c', str(bat)], cwd=root, check=True)
                optimize = ['-' + 'O' * sys.flags.optimize] if sys.flags.optimize else []
                command = [sys.executable, *optimize, '-B', str(Path(__file__).resolve()), '--worker', str(dll), '--decoder', str(a.decoder), '--image', str(a.image)]
                if name != 'actual': command.append('--mutant')
                subprocess.run(command, cwd=root, check=True)
                print(lang, name, 'passed', flush=True)
    need(hashlib.sha256(a.candidate.read_bytes()).hexdigest() == source_hash, 'candidate source changed')
    print('LIMIT: host and successful-read fixture only; final-value checks do not detect transient writes; not target CPU, ABI, reachability or device proof')


if __name__ == '__main__': main()
