#!/usr/bin/env python3
"""Inspect actual optimized RV32 objects, not a target execution or ABI proof."""
import argparse
import hashlib
from pathlib import Path
import runpy
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ELF = runpy.run_path(str(ROOT / 'src/native/tx_candidate/postpass/elf32.py'))['ELF']
U32 = 0xffffffff


def need(condition, message):
    if not condition:
        raise ValueError(message)


def decode(code, pc):
    need(len(code) == 10 and code[8:] == b'\x82\x80', 'expected 10-byte leaf ending in c.jr ra')
    a = int.from_bytes(code[:4], 'little')
    b = int.from_bytes(code[4:8], 'little')
    opcode, rd = a & 127, (a >> 7) & 31
    need(opcode in (0x17, 0x37) and rd != 0, 'expected auipc/lui')
    need(b & 0x707f == 0x23, 'expected sb')
    rs1, rs2 = (b >> 15) & 31, (b >> 20) & 31
    immediate = ((b >> 25) << 5) | ((b >> 7) & 31)
    if immediate & 0x800:
        immediate -= 0x1000
    base = ((pc if opcode == 0x17 else 0) + (a & 0xfffff000)) & U32
    need(rs1 == rd and rs2 == 10, 'SB must use computed base and a0')
    return {'opcode':opcode, 'scratch':rd, 'address':(base + immediate) & U32}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--tool-dir', required=True, type=Path)
    args = p.parse_args()
    raw = (ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
    need(len(raw)==76800 and hashlib.sha256(raw).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667', 'BIN identity')
    leaf = (HERE/'leaf.c').read_bytes()
    need(hashlib.sha256(leaf).hexdigest()=='81dde947df04c123617fa2fa326ca7f2a78544b461fabbb8ba64ae5a1cd74a4a', 'source identity')
    original = decode(raw[0xb0b0-0x8000:0xb0ba-0x8000], 0xb0b0)
    need(original == {'opcode':0x17, 'scratch':15, 'address':0x2000beeb}, 'original encoding differs')
    clang = args.tool_dir/'clang.exe'
    with tempfile.TemporaryDirectory() as td:
        for language, std in [('c','c11'),('c++','c++17')]:
            for opt in ('-O2','-Oz'):
                obj = Path(td)/(std+opt+'.o')
                cmd = [str(clang),'-target','riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-x',language,'-std='+std,opt,'-c',str(HERE/'leaf.c'),'-o',str(obj)]
                result = subprocess.run(cmd, capture_output=True, text=True)
                need(result.returncode == 0, 'clang failed: '+result.stderr)
                e = ELF(obj)
                syms = [s for s in e.symbols if s['info'] & 15 == 2 and s['size'] and s['index'] not in (0,0xfff1)]
                need(len(syms)==1 and not e.relocations, 'unexpected functions or relocations')
                code = e.function_bytes(syms[0])
                target = decode(code,0xb0b0)
                need(target == {'opcode':0x37, 'scratch':11, 'address':0x2000beeb}, 'optimized codegen changed')
                need(code != raw[0xb0b0-0x8000:0xb0ba-0x8000], 'unexpected byte identity')
                print(f'PASS {std} {opt}: 10-byte leaf stores a0 low byte at 0x2000beeb; no relocations; original clobbers a5, candidate clobbers a1')
    print('LIMIT: observed compiler output and decoded register/store effects only; not byte-exact, target ABI equivalence, memory-map validation, or hardware')


if __name__ == '__main__':
    main()
