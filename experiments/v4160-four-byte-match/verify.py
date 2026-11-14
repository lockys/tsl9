import argparse
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
WINDOW = bytes.fromhex('91 47 e3 9a f6 f6 b7 67 42 62 93 87 17 14 3e d8 93 87 41 05 90 43 91 46 81 47 33 07 f4 00 b3 05 f6 00 03 47 07 00 83 c5 c5 00 63 8c e5 00 0c 18 be 95 83 c5 05 00 63 86 e5 00 01 46 93 05 80 0a 65 bf 85 07 e3 9b d7 fc 85 45 26 85 ef f0 1f ca 01 45 ef f0 1f c6 05 b7')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vcvars', required=True, type=Path)
    args = parser.parse_args()
    image = IMAGE.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667':
        raise ValueError('firmware identity mismatch')
    if image[0x14122-0x8000:0x1417a-0x8000] != WINDOW:
        raise ValueError('instruction window mismatch')
    print('PASS: pinned BIN and 88-byte instruction window', flush=True)
    with tempfile.TemporaryDirectory(prefix='tsl9-four-byte-') as temp:
        batch = Path(temp) / 'build.bat'
        for name, flags in (('C', '/TC /std:c11'), ('C++', '/TP /std:c++17')):
            exe = Path(temp) / 'test.exe'
            batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 {flags} "{HERE / "model.c"}" "{HERE / "test.c"}" /Fe:"{exe}"\n@exit /b %errorlevel%\n', encoding='utf-8')
            subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=temp, check=True)
            print(name + ': ', end='', flush=True)
            subprocess.run([str(exe)], check=True)
            dll = Path(temp) / 'model.dll'
            batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{HERE / "model.c"}" /Fe:"{dll}"\n@exit /b %errorlevel%\n', encoding='utf-8')
            subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=temp, check=True)
            print(name + ' byte differential: ', end='', flush=True)
            subprocess.run([sys.executable, '-B', str(HERE / 'differential.py'), str(dll)], check=True)
    print('Bounded byte decoder and host model; no hardware execution.')


if __name__ == '__main__': main()
