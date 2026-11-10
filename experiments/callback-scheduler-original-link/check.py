#!/usr/bin/env python3
"""Isolated, offline direct-object original-VA composition; never execute target code."""
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
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module
first = load('first', 'experiments/callback-901a-original-link/check.py')
second = load('second', 'experiments/callback-907a-original-link/check.py')
sched = load('sched', 'experiments/scheduler-9124-original-link/check.py')
CALLBACK_HASH = '3c5d7a3cb3c02e301c158c136a1cdbb1a70839100f2b54bb89431160d92bfeb2'
NAMES = ['tsl9_callback_table_' + n for n in first.NAMES + second.NAMES] + sched.NAMES
ADDR = first.ADDR[:-1] + second.ADDR[:-1] + sched.ADDR
MUTATIONS = {'callback-early': (0, 'CALL_PORT("li s0, 0");\n    a4 = UINT32_C(15); LIVE;', 'CALL_PORT("li s0, 0");\n    a4 = UINT32_C(14); LIVE;'),
             'callback-late': (0, 'a2 = UINT32_C(180); LIVE;', 'a2 = UINT32_C(179); LIVE;'),
             'scheduler': (1, 'a5=625; KEEP(a5);', 'a5=624; KEEP(a5);')}

def link(cmd, ok=True, message=None):
    p = subprocess.run([str(x) for x in cmd], capture_output=True, text=True)
    if ok:
        assert p.returncode == 0, p.stdout + p.stderr
    else:
        assert p.returncode != 0 and message in (p.stdout + p.stderr), p.stdout + p.stderr

def inspect(path):
    data = path.read_bytes()
    h = struct.unpack_from('<16sHHIIIIIHHHHHH', data)
    assert h[0][:7] == b'\x7fELF\x01\x01\x01' and h[1:3] == (2, 243)
    sections = [struct.unpack_from('<10I', data, h[6]+i*h[11]) for i in range(h[12])]
    code = [s for s in sections if s[3] == 0x901a and s[5] == 566 and s[2] & 4]
    assert len(code) == 1
    tables = [s for s in sections if s[1] == 2]; assert len(tables) == 1
    table = tables[0]; strings = sections[table[6]]; names = data[strings[4]:strings[4]+strings[5]]
    symbols = {}
    for off in range(table[4], table[4]+table[5], table[9]):
        n,v,size,info,other,sh = struct.unpack_from('<IIIBBH', data, off)
        if n:
            name = names[n:names.index(b'\0',n)].decode()
            assert sh != 0, name
            if info >> 4:
                assert name not in symbols, name
                symbols[name] = (v,size,sh)
    for i,name in enumerate(NAMES):
        v,size,sh = symbols[name]
        assert (v,size) == (ADDR[i],ADDR[i+1]-ADDR[i]) and sections[sh] == code[0], name
    # Decode each no-relax AUIPC/JALR call in the separate probe object.
    v,size,sh = symbols['probe_calls']; assert (v,size) == (0x8000, 24)
    sec = sections[sh]; off = sec[4]+v-sec[3]
    for i,target in enumerate(('tsl9_callback_table_entry_901a','tsl9_callback_external_9124','probe_external_stub')):
        auipc,jalr = struct.unpack_from('<II', data, off+i*8)
        assert auipc & 0xfff == 0x97 and jalr & 0xfffff == 0x080e7
        hi = struct.unpack('<i', struct.pack('<I', auipc & 0xfffff000))[0]
        lo = struct.unpack('<i', struct.pack('<I', jalr & 0xfff00000))[0] >> 20
        assert (v+i*8+hi+lo) & 0xffffffff == symbols[target][0]
    assert symbols['probe_external_stub'][:2] == (0x8020, 2)
    s = code[0]; return data[s[4]:s[4]+s[5]]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ndk-bin', type=pathlib.Path, default=sched.DEFAULT_TOOLS); args = ap.parse_args()
    callback = first.SOURCE.read_bytes(); assert hashlib.sha256(callback).hexdigest() == CALLBACK_HASH
    scheduler = sched.checked(sched.SOURCE, 'source')
    texts = [callback.decode('utf-8'), scheduler.decode('utf-8')]
    for text in texts: assert not any(x in text for x in ('.byte', '.2byte', '.4byte', '.word', '.insn'))
    for index,before,after in MUTATIONS.values(): assert texts[index].count(before) == 1 and before != after
    image = sched.checked(sched.REFERENCE, 'reference'); ref = image[0x101a:0x1250]; assert len(ref) == 566
    for tool in ('clang.exe','ld.lld.exe'): sched.checked(args.ndk_bin/tool, tool)
    include = args.ndk_bin.parent/'lib/clang/18/include'
    assert hashlib.sha256((include/'stdint.h').read_bytes()).hexdigest() == '7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
    with tempfile.TemporaryDirectory(prefix='combined-proof-') as tmp:
        d = pathlib.Path(tmp)
        sections = ''.join(f'KEEP(*{"callback.o" if i < len(first.NAMES)+len(second.NAMES) else "scheduler.o"}(.text.{n}))\n' for i,n in enumerate(NAMES))
        (d/'layout.ld').write_text('SECTIONS { .probe 0x8000 : { *(.text.probe) } .stub 0x8020 : { *(.text.stub) } .text 0x901a : {\n'+sections+'} }\nASSERT(SIZEOF(.text) == 566, "missing source sections")\n')
        (d/'probe.S').write_text('.section .text.probe,"ax",@progbits\n.globl probe_calls\n.type probe_calls,@function\nprobe_calls:\n.option push\n.option norelax\ncall tsl9_callback_table_entry_901a\ncall tsl9_callback_external_9124\ncall probe_external_stub\n.option pop\n.size probe_calls,.-probe_calls\n')
        (d/'stub.S').write_text('.section .text.stub,"ax",@progbits\n.globl probe_external_stub\n.type probe_external_stub,@function\nprobe_external_stub:\nret\n.size probe_external_stub,.-probe_external_stub\n')
        for name in ('probe','stub'):
            sched.run([args.ndk_bin/'clang.exe', *sched.FLAGS, '-c', d/(name+'.S'), '-o', d/(name+'.o')])
        assert first.object_relocations(d/'probe.o') == sorted([('.text.probe', 0, 19, 'tsl9_callback_table_entry_901a', 0), ('.text.probe', 8, 19, 'tsl9_callback_external_9124', 0), ('.text.probe', 16, 19, 'probe_external_stub', 0)])
        for mode in ('c','cpp'):
            language = ['-x','c','-std=c11'] if mode == 'c' else ['-x','c++','-std=c++17','-fno-exceptions','-fno-rtti']
            for mutation in ('none', *MUTATIONS):
                for i,(name,source) in enumerate((('callback',first.SOURCE),('scheduler',sched.SOURCE))):
                    if mutation != 'none' and MUTATIONS[mutation][0] == i:
                        _,before,after = MUTATIONS[mutation]; source = d/'mutation.c'; source.write_text(texts[i].replace(before,after), encoding='utf-8')
                    sched.run([args.ndk_bin/'clang.exe', *sched.FLAGS, '-nostdinc','-isystem',include,*language,'-c',source,'-o',d/(name+'.o')])
                # Exact relocation list proves the callback source does not itself reference scheduler.
                callback_relocs = first.object_relocations(d/'callback.o')
                assert len(callback_relocs) == 8 and all(r[3].startswith('tsl9_callback_table_') for r in callback_relocs)
                cmd = [args.ndk_bin/'ld.lld.exe','--no-relax','--no-undefined','-T',d/'layout.ld','-o',d/'linked.elf',d/'probe.o',d/'stub.o',d/'callback.o',d/'scheduler.o']
                link(cmd); got = inspect(d/'linked.elf')
                diffs = [hex(0x901a+i) for i,(a,b) in enumerate(zip(got,ref)) if a != b]
                assert bool(diffs) == (mutation != 'none'), (mode, mutation, diffs)
                print(mode, mutation, 'rejected' if diffs else 'exact', diffs)
            for missing in ('callback.o','scheduler.o','stub.o'):
                cmd = [args.ndk_bin/'ld.lld.exe','--no-relax','--no-undefined','-T',d/'layout.ld','-o',d/'missing.elf'] + [d/n for n in ('probe.o','stub.o','callback.o','scheduler.o') if n != missing]
                expected = {'callback.o':'tsl9_callback_table_entry_901a','scheduler.o':'tsl9_callback_external_9124','stub.o':'probe_external_stub'}[missing]
                link(cmd, False, expected); print(mode, 'missing', missing, 'rejected')
    print('window sha256:', hashlib.sha256(ref).hexdigest())
if __name__ == '__main__': main()
