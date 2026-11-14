#!/usr/bin/env python3
"""Compile and execute the existing injected-destination harness; host only."""
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
LEAF_SHA = '81dde947df04c123617fa2fa326ca7f2a78544b461fabbb8ba64ae5a1cd74a4a'


def run(cmd, cwd):
    p = subprocess.run([str(v) for v in cmd], cwd=cwd, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError('command failed: ' + ' '.join(map(str, cmd)) + '\n' + p.stdout + p.stderr)


def main():
    compiler = shutil.which('cl')
    if not compiler:
        raise RuntimeError('MSVC cl not found; run inside a Visual Studio developer command prompt')
    leaf = (HERE / 'leaf.c').read_bytes()
    if hashlib.sha256(leaf).hexdigest() != LEAF_SHA:
        raise ValueError('candidate source identity mismatch')
    harness = (HERE / 'host_harness.c').read_bytes()
    old = b'B0B0_DESTINATION = (uint8_t)value;'
    if leaf.count(old) != 1:
        raise ValueError('candidate mutation site mismatch')
    variants = {
        'original': leaf,
        'flip-low-bit': leaf.replace(old, b'B0B0_DESTINATION = (uint8_t)(value ^ 1u);'),
        'write-adjacent': leaf.replace(old, b'B0B0_DESTINATION = (uint8_t)value; HOST_B0B0_MEMORY[0] = 0;'),
    }
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / 'host_harness.c').write_bytes(harness)
        for mode, flags in [('C11', ['/TC','/std:c11']), ('C++17', ['/TP','/std:c++17'])]:
            for opt in ('/Od', '/O2'):
                for name, source in variants.items():
                    (root / 'leaf.c').write_bytes(source)
                    exe = root / 'harness.exe'
                    if exe.exists():
                        exe.unlink()
                    run([compiler, '/nologo', '/W4', '/WX', *flags, opt, 'host_harness.c', '/Fe:' + str(exe)], root)
                    p = subprocess.run([str(exe)], cwd=root, capture_output=True)
                    if (p.returncode == 0) != (name == 'original'):
                        raise ValueError(f'{mode} {opt}: unexpected result for {name}: {p.returncode}')
                    print(f'PASS {mode} {opt}: {name} ' + ('succeeded (768 cases)' if name == 'original' else 'rejected'))
    print('LIMIT: host injected destination only; does not establish target ABI, codegen, addresses or hardware')


if __name__ == '__main__':
    main()
