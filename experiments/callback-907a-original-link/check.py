#!/usr/bin/env python3
"""Offline original-VA source-object link; never execute on target."""
import argparse
import hashlib
import importlib.util
import pathlib
import struct
import subprocess
import sys
import tempfile

if not __debug__:
    sys.exit('assertions required; do not use python -O')

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('prior', ROOT / 'experiments/callback-901a-original-link/check.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
NAMES = ['entry_907a', 'block_9096', 'block_90a4', 'entry_90b0', 'block_90c6', 'block_90cc', 'block_90d8', 'block_90e0', 'block_9110', 'block_9118']
ADDR = [0x907a, 0x9096, 0x90a4, 0x90b0, 0x90c6, 0x90cc, 0x90d8, 0x90e0, 0x9110, 0x9118, 0x9124]
RELOCS = sorted([
    ('.text.tsl9_callback_table_block_90c6', 2, 16, 'tsl9_callback_table_block_9110', 0),
    ('.text.tsl9_callback_table_block_90cc', 10, 44, 'tsl9_callback_table_block_90e0', 0),
    ('.text.tsl9_callback_table_block_9110', 4, 16, 'tsl9_callback_table_block_90c6', 0),
])

def linked(path):
    data = path.read_bytes()
    h = struct.unpack_from('<16sHHIIIIIHHHHHH', data)
    assert h[0][:7] == b'\x7fELF\x01\x01\x01' and h[1] == 2 and h[2] == 243
    sections = [struct.unpack_from('<10I', data, h[6]+i*h[11]) for i in range(h[12])]
    code = [s for s in sections if s[3] == ADDR[0] and s[5] == ADDR[-1]-ADDR[0] and s[2] & 4]
    assert len(code) == 1
    tables = [s for s in sections if s[1] == 2]; assert len(tables) == 1
    table = tables[0]; strings = sections[table[6]]; names = data[strings[4]:strings[4]+strings[5]]
    symbols = {}
    for off in range(table[4], table[4]+table[5], table[9]):
        n,v,size,info,other,sh = struct.unpack_from('<IIIBBH', data, off)
        if n:
            name = names[n:names.index(b'\0',n)].decode()
            assert sh != 0, ('undefined symbol', name)
            symbols[name] = (v,size,sh)
    for i,name in enumerate(NAMES):
        v,size,sh = symbols['tsl9_callback_table_'+name]
        assert (v,size) == (ADDR[i],ADDR[i+1]-ADDR[i]) and sections[sh] == code[0], name
    s = code[0]
    return data[s[4]:s[4]+s[5]]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ndk-bin', type=pathlib.Path, default=prior.TOOLS); args=ap.parse_args()
    image = prior.BIN.read_bytes()
    assert hashlib.sha256(image).hexdigest() == '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
    reference = image[0x107a:0x1124]
    assert hashlib.sha256(reference).hexdigest() == 'cd049b87b5048a5467868d04b256066222b8db194a0c4eb60d5d2d77cce05a17'
    source = prior.SOURCE.read_text(encoding='utf-8')
    marker = '/* Original 907A..9096 */'
    assert source.count(marker) == 1
    text = source.split('/* Original 901A..9026 */')[0] + marker + source.split(marker)[1]
    assert not any(d in text for d in ('.byte', '.2byte', '.4byte', '.word', '.insn'))
    mutations = {
        'semantic': ('a2 = UINT32_C(180); LIVE;', 'a2 = UINT32_C(179); LIVE;'),
        'branch-condition': ('bne a3,a0,.Lcallback_edge_90c8', 'beq a3,a0,.Lcallback_edge_90c8'),
        'branch-target': ('R_RISCV_RVC_BRANCH,tsl9_callback_table_block_90e0', 'R_RISCV_RVC_BRANCH,tsl9_callback_table_block_9118'),
        'unresolved': ('R_RISCV_RVC_BRANCH,tsl9_callback_table_block_90e0', 'R_RISCV_RVC_BRANCH,missing_callback_target'),
    }
    for before,_ in mutations.values(): assert text.count(before) == 1
    with tempfile.TemporaryDirectory() as tmp:
        d = pathlib.Path(tmp)
        (d/'layout.ld').write_text('SECTIONS { .text 0x907a : {\n' + ''.join('KEEP(*(.text.tsl9_callback_table_'+n+'))\n' for n in NAMES) + '} }\n')
        for mode in ('c','cpp'):
            for mutation in ('none', *mutations):
                src=d/'input.c'; obj=d/'input.o'; elf=d/'linked.elf'
                src.write_text(text if mutation == 'none' else text.replace(*mutations[mutation]), encoding='utf-8')
                language = ['-x','c++','-std=c++17','-fno-exceptions','-fno-rtti'] if mode == 'cpp' else ['-x','c','-std=c11']
                prior.run([args.ndk_bin/'clang.exe', *prior.FLAGS, *language, '-c', src, '-o', obj])
                relocs = prior.object_relocations(obj)
                if mutation in ('branch-target', 'unresolved'):
                    assert relocs != RELOCS
                else:
                    assert relocs == RELOCS, (mutation, relocs)
                cmd = [str(x) for x in [args.ndk_bin/'ld.lld.exe', '--no-relax', '--no-undefined', '-T', d/'layout.ld', '-o', elf, obj]]
                p = subprocess.run(cmd, capture_output=True, text=True)
                if mutation == 'unresolved':
                    assert p.returncode != 0 and 'missing_callback_target' in p.stderr, p.stderr
                    print(mode, mutation, 'link rejected'); continue
                assert p.returncode == 0, p.stderr
                got = linked(elf)
                diffs = [hex(ADDR[0]+i) for i,(a,b) in enumerate(zip(got,reference)) if a != b]
                assert bool(diffs) == (mutation != 'none'), (mutation, diffs)
                print(mode, mutation, 'rejected' if diffs else 'exact match', diffs)

if __name__ == '__main__': main()
