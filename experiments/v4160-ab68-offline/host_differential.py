#!/usr/bin/env python3
"""Host test of a transformed AB68 candidate; not target CPU or ABI."""
import argparse
import ctypes
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import caller_sites

HERE = Path(__file__).resolve().parent
CANDIDATE_SHA = 'd27b7e74fee4b2de737e53a21884c99179cb3d05e70c84301ba1dd7a1d4a481b'
BIN = HERE.parents[1] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
LEAF = bytes.fromhex('17150020034505388280')

def need(ok, message):
    if not ok:
        raise ValueError(message)

def worker(path, mutant):
    lib = ctypes.CDLL(str(path))
    lib.set_value.argtypes = [ctypes.c_ubyte]
    lib.get_value.restype = ctypes.c_ubyte
    lib.call_leaf.restype = ctypes.c_uint
    mismatches = 0
    for value in range(256):
        lib.set_value(value)
        actual = lib.call_leaf()
        mismatches += actual != value or lib.get_value() != value
    need((mismatches > 0) == mutant, 'unexpected result')
    print(f'{"mutant rejected" if mutant else "candidate passed"}: 256 inputs, {mismatches} mismatches', flush=True)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--clang', type=Path)
    p.add_argument('--linker', type=Path)
    p.add_argument('--worker', type=Path)
    p.add_argument('--mutant', action='store_true')
    a = p.parse_args()
    if a.worker:
        worker(a.worker, a.mutant)
        return
    if not a.clang or not a.linker:
        p.error('--clang and --linker required')
    image = BIN.read_bytes()
    need(hashlib.sha256(image).hexdigest() == caller_sites.SHA256, 'image identity')
    need(image[0xab68-0x8000:0xab68-0x8000+10] == LEAF, 'leaf identity')
    raw = (HERE/'candidate.c').read_bytes()
    need(hashlib.sha256(raw).hexdigest() == CANDIDATE_SHA, 'candidate identity')
    source = raw.decode('utf-8')
    anchor = 'extern volatile unsigned char tsl9_ab68_data __attribute__((visibility("hidden")));'
    need(source.count(anchor) == 1, 'storage anchor')
    source = source.replace(anchor, 'volatile unsigned char tsl9_ab68_data;')
    expression = 'return tsl9_ab68_data;'
    need(source.count(expression) == 1, 'return anchor')
    variants = {'candidate': source,
                'signed': source.replace(expression, 'return (signed char)tsl9_ab68_data;'),
                'increment': source.replace(expression, 'return tsl9_ab68_data + 1;'),
                'constant': source.replace(expression, 'return 0;')}
    need(len(set(variants.values())) == 4, 'mutation anchors')
    fixture = '''\n#ifdef __cplusplus
extern "C" {
#endif
__declspec(dllexport) void set_value(unsigned char x) { tsl9_ab68_data=x; }
__declspec(dllexport) unsigned char get_value(void) { return tsl9_ab68_data; }
__declspec(dllexport) unsigned int call_leaf(void) { return tsl9_ab68(); }
#ifdef __cplusplus
}
#endif
'''
    with tempfile.TemporaryDirectory(prefix='tsl9-ab68-host-') as tmp:
        root = Path(tmp)
        for lang, std in (('c', 'c11'), ('c++', 'c++17')):
            for name, code in variants.items():
                unit, obj, dll = root/'unit.c', root/'unit.obj', root/'unit.dll'
                unit.write_text(code+fixture, encoding='utf-8')
                subprocess.run([str(a.clang.resolve()), '--target=x86_64-pc-windows-msvc', '-c', '-x', lang, '-std='+std, '-O2', str(unit), '-o', str(obj)], check=True, cwd=root)
                subprocess.run([str(a.linker.resolve()), '/nologo', '/dll', '/noentry', '/nodefaultlib', str(obj), '/out:'+str(dll)], check=True, cwd=root)
                cmd = [sys.executable, *(['-'+'O'*sys.flags.optimize] if sys.flags.optimize else []), '-B', str(Path(__file__).resolve()), '--worker', str(dll)]
                if name != 'candidate':
                    cmd.append('--mutant')
                print(lang, name, flush=True)
                subprocess.run(cmd, check=True, cwd=root)
    need((HERE/'candidate.c').read_bytes() == raw, 'candidate changed')
    print('LIMIT: transformed binding and host final byte only; not target ABI, all memory, transient writes or device')

if __name__ == '__main__':
    main()
