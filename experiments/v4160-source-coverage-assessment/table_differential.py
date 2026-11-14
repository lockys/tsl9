"""Compare C/C++ table projection with pinned APP dispatch; temporary DLLs only."""
import argparse
import ctypes
import hashlib
import importlib.util
from pathlib import Path
import random
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('dispatch', HERE / 'table_dispatch.py')
dispatch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dispatch)


def worker(dll, mutant):
    image = dispatch.IMAGE.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != dispatch.SHA:
        raise ValueError('APP identity mismatch')
    code = image[dispatch.START-0x8000:dispatch.START-0x8000+len(dispatch.EXPECTED)]
    original = image[0x1a6a4-0x8000:0x1a6b8-0x8000]
    byte = ctypes.c_uint8
    fn = ctypes.CDLL(str(dll)).tsl9_table_dispatch
    fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(byte)]
    fn.restype = ctypes.c_uint32
    def equal(index, table):
        result = fn(index, (byte * 20).from_buffer_copy(table))
        return result == dispatch.dispatch(code, table, index)
    if mutant:
        if all(equal(i, original) for i in range(256)):
            raise ValueError('mutant not detected')
        print('PASS: semantic mutant rejected', flush=True)
        return
    rng = random.Random(0x41614512)
    for index in range(256):
        if not equal(index, original): raise ValueError('original table mismatch')
    # A NULL table is valid only here: out-of-range dispatch must not read it.
    for index in range(5, 256):
        if fn(index, None) != 0x14098: raise ValueError('unexpected table read or exit')
    for n in range(20000):
        index = rng.randrange(5) if n % 2 == 0 else rng.randrange(5,256)
        table = rng.randbytes(20)
        if not equal(index, table): raise ValueError('synthetic table mismatch')
    print('PASS: 256 original byte indices, 251 no-table exits, and 20000 synthetic table/index cases', flush=True)


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars', type=Path)
    group.add_argument('--worker', type=Path)
    parser.add_argument('--mutant', action='store_true')
    args = parser.parse_args()
    if args.worker:
        worker(args.worker, args.mutant)
        return
    source = (HERE / 'table_model.c').read_text(encoding='utf-8')
    changes = [('bound', 'index > 4u', 'index >= 4u'),
               ('wrong_base', '0x1a6a4', '0x1a6a0'),
               ('index', '4u * index', '4u * (index < 4u ? (index ^ 1u) : index)')]
    variants = [('base', source)]
    for name, old, new in changes:
        if source.count(old) != 1: raise ValueError('ambiguous mutant')
        variants.append((name, source.replace(old,new)))
    with tempfile.TemporaryDirectory(prefix='tsl9-table-model-') as temp:
        folder = Path(temp)
        for label, flags in (('C','/TC /std:c11'), ('Cpp','/TP /std:c++17')):
            for name, text in variants:
                src = folder / (label+name+'.c'); dll = folder / (label+name+'.dll'); batch = folder / 'build.bat'
                src.write_text(text, encoding='utf-8')
                batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{src}" /Fe:"{dll}"\n@exit /b %errorlevel%\n', encoding='utf-8')
                subprocess.run(['cmd.exe','/d','/c',str(batch)], cwd=folder, check=True)
                command = [sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)]
                if name != 'base': command.append('--mutant')
                subprocess.run(command, check=True)
    print('Successful reads assumed; synthetic tables are not claimed reachable.')

if __name__ == '__main__': main()
