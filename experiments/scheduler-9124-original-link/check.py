#!/usr/bin/env python3
"""Isolated original-VA source-object comparison; never executes target code."""
import argparse, hashlib, pathlib, struct, subprocess, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src/native/receive/scheduler.c'
REFERENCE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
DEFAULT_TOOLS = pathlib.Path(r'C:\Users\locky\AppData\Local\Android\Sdk\ndk\27.1.12297006\toolchains\llvm\prebuilt\windows-x86_64\bin')
PINS = {'source': '95d54f0277f717f7b79dc49a1b55f7e4988e05ffdb6dd53e9195153159b94457', 'reference': '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667', 'clang.exe': '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6', 'ld.lld.exe': 'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f'}
FLAGS = ['--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-mno-relax','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-fno-pic','-ffunction-sections','-Oz','-Wall','-Wextra','-Werror']
ADDR = [0x9124,0x913a,0x913c,0x913e,0x9142,0x914a,0x9150,0x9152,0x915c,0x9164,0x916e,0x9180,0x9188,0x919c,0x91a2,0x91ae,0x91b6,0x91d0,0x91ea,0x91fe,0x9206,0x920a,0x920e,0x922c,0x9230,0x9234,0x9244,0x924c,0x9250]
NAMES = ['tsl9_callback_external_9124'] + [f'tsl9_scheduler_{a:x}' for a in ADDR[1:-1]]
MUTATIONS = {'semantic': ('a5=625; KEEP(a5);', 'a5=624; KEEP(a5);'), 'branch-condition': ('CBRANCH(c.bnez,a2,tsl9_scheduler_9244);', 'CBRANCH(c.beqz,a2,tsl9_scheduler_9244);'), 'branch-target': ('CBRANCH(c.bnez,a2,tsl9_scheduler_9244);', 'CBRANCH(c.bnez,a2,tsl9_scheduler_922c);')}

def run(cmd):
    p = subprocess.run([str(x) for x in cmd], capture_output=True, text=True)
    if p.returncode: raise RuntimeError(f'command failed: {cmd}\n{p.stdout}{p.stderr}')

def checked(path, pin):
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != PINS[pin]: raise RuntimeError(f'{pin} hash mismatch: {digest}')
    return data

def extract(path):
    data = path.read_bytes()
    h = struct.unpack_from('<16sHHIIIIIHHHHHH', data)
    assert h[0][:7] == b'\x7fELF\x01\x01\x01' and h[1:3] == (2,243)
    sections = [struct.unpack_from('<10I', data, h[6]+i*h[11]) for i in range(h[12])]
    code = [s for s in sections if s[3] == 0x9124 and s[5] == 0x12c and s[2] & 4]
    assert len(code) == 1, 'wrong output address/size'
    sym = [s for s in sections if s[1] == 2]; assert len(sym) == 1
    s = sym[0]; st = sections[s[6]]; names = data[st[4]:st[4]+st[5]]
    symbols = {}
    for off in range(s[4], s[4]+s[5], s[9]):
        n,v,size,info,other,sh = struct.unpack_from('<IIIBBH',data,off)
        if n: symbols[names[n:names.index(b'\0',n)].decode()] = (v,size,sh)
    for i,name in enumerate(NAMES):
        assert symbols[name][:2] == (ADDR[i], ADDR[i+1]-ADDR[i]), (name, symbols[name])
        assert sections[symbols[name][2]] == code[0]
    s = code[0]
    return data[s[4]:s[4]+s[5]]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ndk-bin', type=pathlib.Path, default=DEFAULT_TOOLS); args = ap.parse_args()
    text = checked(SOURCE, 'source').decode('utf-8')
    original = checked(REFERENCE, 'reference')
    ref = original[0x9124-0x8000:0x9250-0x8000]; assert len(ref) == 0x12c
    for tool in ('clang.exe','ld.lld.exe'): checked(args.ndk_bin/tool, tool)
    include = args.ndk_bin.parent/'lib/clang/18/include'
    assert hashlib.sha256((include/'stdint.h').read_bytes()).hexdigest() == '7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
    assert not any(x in text for x in ('.byte', '.2byte', '.4byte', '.word', '.insn'))
    for before, after in MUTATIONS.values(): assert text.count(before) == 1 and before != after
    with tempfile.TemporaryDirectory(prefix='scheduler-proof-') as tmp:
        d = pathlib.Path(tmp)
        layout = 'SECTIONS { .text 0x9124 : {\n' + ''.join(f'KEEP(*(.text.{name}))\n' for name in NAMES) + '} }\n'
        (d/'layout.ld').write_text(layout)
        for mode in ('c','cpp'):
            language = ['-x','c','-std=c11'] if mode == 'c' else ['-x','c++','-std=c++17','-fno-exceptions','-fno-rtti']
            for mutation in ('none', *MUTATIONS):
                src = SOURCE
                if mutation != 'none':
                    src = d/'mutation.c'; src.write_text(text.replace(*MUTATIONS[mutation]), encoding='utf-8')
                obj, elf = d/'source.o', d/'linked.elf'
                run([args.ndk_bin/'clang.exe', *FLAGS, '-nostdinc', '-isystem', include, *language, '-c', src, '-o', obj])
                run([args.ndk_bin/'ld.lld.exe','--no-relax','-T',d/'layout.ld','-o',elf,obj])
                got = extract(elf)
                diffs = [hex(0x9124+i) for i,(a,b) in enumerate(zip(got,ref)) if a != b]
                if bool(diffs) != (mutation != 'none'): raise AssertionError((mode, mutation, diffs))
                print(mode, mutation, 'rejected' if diffs else 'exact', 'differences:', diffs)
    print('reference window sha256:', hashlib.sha256(ref).hexdigest())

if __name__ == '__main__': main()
