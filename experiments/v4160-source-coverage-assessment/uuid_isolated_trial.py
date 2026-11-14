#!/usr/bin/env python3
"""Isolated typed UUID experiment; never changes curated source or proves C type compatibility."""
import argparse
import hashlib
from pathlib import Path
import runpy
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
ELF = runpy.run_path(str(ROOT / 'src/native/tx_candidate/postpass/elf32.py'))['ELF']
NAME = 'tsl9_opaque_gap_0001ab44'
OLD = '''TSL9_OPAQUE_LINKAGE const uint8_t tsl9_opaque_gap_0001ab44[4]
    __attribute__((used, aligned(1), section(".rodata.tsl9_opaque_gap_0001ab44"))) = {
    0xf1, 0xff, 0x00, 0x00
};'''
NEW = '''struct trial_uuid_storage { uint16_t uuid; uint8_t unknown[2]; };
#if !defined(__BYTE_ORDER__) || __BYTE_ORDER__ != __ORDER_LITTLE_ENDIAN__
#error "This UUID trial requires little endian"
#endif
#ifdef __cplusplus
static_assert(sizeof(struct trial_uuid_storage)==4 && __builtin_offsetof(struct trial_uuid_storage,unknown)==2, "trial layout");
#else
_Static_assert(sizeof(struct trial_uuid_storage)==4 && __builtin_offsetof(struct trial_uuid_storage,unknown)==2, "trial layout");
#endif
TSL9_OPAQUE_LINKAGE const struct trial_uuid_storage tsl9_opaque_gap_0001ab44
    __attribute__((used, aligned(2), section(".rodata.tsl9_opaque_gap_0001ab44"))) = {
    UINT16_C(0xfff1), {0, 0}
};'''


def invoke(args):
    p = subprocess.run([str(x) for x in args], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr)


def sections(e):
    return {s['name']: (s['size'], s['flags'], e.data(s)) for s in e.sections if s['name'].startswith('.rodata.tsl9')}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tool-dir', type=Path, required=True)
    a = parser.parse_args()
    rootfile = ROOT / 'src/native/receive/opaque_allowed_gaps.c'
    source = rootfile.read_text(encoding='utf-8')
    if source.count(OLD) != 1:
        raise ValueError('expected exactly one original byte-array definition')
    raw = (ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
    if hashlib.sha256(raw).hexdigest() != '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667' or raw[0x1ab44-0x8000:0x1ab48-0x8000] != bytes.fromhex('f1ff0000'):
        raise ValueError('original BIN mismatch')
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        original, trial, consumer = p/'original.c', p/'trial.c', p/'consumer.c'
        original.write_text(source, encoding='utf-8')
        trial.write_text(source.replace(OLD, NEW), encoding='utf-8')
        consumer.write_text('#include <stdint.h>\n#ifdef __cplusplus\nextern "C" {\n#endif\nextern const uint8_t '+NAME+'[4];\nconst uint8_t *legacy_pointer = '+NAME+';\n#ifdef __cplusplus\n}\n#endif\n', encoding='utf-8')
        for mode, language, std in [('c','c','c11'), ('cpp','c++','c++17')]:
            common = [a.tool_dir/'clang.exe', '-target','riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-x',language,'-std='+std,'-c']
            before, after, use, linked = (p/(mode+x) for x in ('-before.o','-after.o','-use.o','-linked.o'))
            invoke(common + [original, '-o', before])
            invoke(common + [trial, '-o', after])
            invoke(common + [consumer, '-o', use])
            orig, changed, consumer_obj = ELF(before), ELF(after), ELF(use)
            x, y = sections(orig), sections(changed)
            if x != y or x['.rodata.'+NAME] != (4, 2, bytes.fromhex('f1ff0000')):
                raise ValueError('trial changed allocated bytes or flags')
            refs = [r for r in consumer_obj.relocations if r['symbol']['name'] == NAME]
            if len(refs) != 1 or refs[0]['symbol']['index'] != 0:
                raise ValueError('unexpected legacy relocation')
            invoke([a.tool_dir/'ld.lld.exe','-m','elf32lriscv','-r','--no-relax',after,use,'-o',linked])
            e = ELF(linked)
            owners = [s for s in e.symbols if s['name'] == NAME]
            refs = [r for r in e.relocations if r['symbol']['name'] == NAME]
            if len(owners)!=1 or owners[0]['size']!=4 or owners[0]['index'] in (0,0xfff1) or len(refs)!=1 or refs[0]['symbol']['index']!=owners[0]['index']:
                raise ValueError('legacy ELF symbol resolution mismatch')
            print(f'PASS {mode}: {len(x)} section bytes and flags match; legacy ELF relocation resolves; C type compatibility not proved')


if __name__ == '__main__':
    main()
