"""Compare host C/C++ semantic projection to bounded original-byte execution."""
import argparse
import _ctypes
import ctypes
import hashlib
from pathlib import Path
import subprocess
import tempfile
from verify import BIN, SHA, run

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vcvars', required=True, type=Path)
    args = parser.parse_args()
    image = BIN.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != SHA:
        raise ValueError('firmware identity mismatch')
    with tempfile.TemporaryDirectory(prefix='tsl9-record-model-') as temp:
        for lang, flags in (('C', '/TC /std:c11'), ('C++', '/TP /std:c++17')):
            dll = Path(temp) / ('record-' + lang.replace('+', 'p') + '.dll')
            batch = Path(temp) / 'build.bat'
            batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{HERE / "model.c"}" /Fe:"{dll}"\n@exit /b %errorlevel%\n', encoding='utf-8')
            subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=temp, check=True)
            library = ctypes.CDLL(str(dll))
            word = ctypes.c_uint32
            fn = library.record_update_a1_one
            fn.argtypes = [word, ctypes.c_uint16, ctypes.c_uint16, ctypes.POINTER(word)]
            fn.restype = None
            count = 0
            for value in list(range(0, 65536, 8)) + [0xffff, 0xfffe, 0x8000, 0x7fff]:
                for handle, first, second in ((value, value, value ^ 1), (value, value ^ 1, value),
                                              (value, value, value), (value, value ^ 1, value ^ 1),
                                              (value | 0x10000, value, value)):
                    reads, writes = run(image, handle, first, second)
                    actual = (word * 8)()
                    fn(handle, first, second, actual)
                    expected = [len(reads)] + reads + [0] * (2-len(reads)) + [len(writes)]
                    expected += [item for event in writes for item in event]
                    expected += [0] * (8-len(expected))
                    if list(actual) != expected:
                        raise ValueError(f'{lang} mismatch: {handle:#x}, {first:#x}, {second:#x}')
                    count += 1
            print(f'PASS {lang}: {count} C model vs original-byte interpreter cases, ordered reads/writes', flush=True)
            handle = library._handle
            del fn, library
            _ctypes.FreeLibrary(handle)
    print('Synthetic successful accesses only; no physical execution or concurrent changes.')


if __name__ == '__main__': main()
