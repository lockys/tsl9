#!/usr/bin/env python3
"""Offline original-VA link check; no target execution."""
import argparse, hashlib, os, pathlib, struct, subprocess, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src/native/receive/callback_table.c'
BIN = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
TOOLS = pathlib.Path(os.environ.get('NDK_LLVM_BIN', r'C:\Users\locky\AppData\Local\Android\Sdk\ndk\27.1.12297006\toolchains\llvm\prebuilt\windows-x86_64\bin'))
FLAGS = ['--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-mno-relax','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-fno-pic','-ffunction-sections','-Oz','-Wall','-Wextra','-Werror']
NAMES = ['entry_901a','block_9026','block_902e','block_9044','block_9050','block_9058','block_905a','block_9066','block_9070','block_9076']
ADDR = [0x901a,0x9026,0x902e,0x9044,0x9050,0x9058,0x905a,0x9066,0x9070,0x9076,0x907a]
def run(cmd):
    p = subprocess.run([str(x) for x in cmd], capture_output=True, text=True)
    if p.returncode: raise RuntimeError('command failed: '+str(cmd)+'\n'+p.stderr)

def object_relocations(path):
    data = path.read_bytes()
    h = struct.unpack_from('<16sHHIIIIIHHHHHH', data)
    assert h[0][:7] == b'\x7fELF\x01\x01\x01' and h[1] == 1 and h[2] == 243
    sections = [struct.unpack_from('<10I', data, h[6]+i*h[11]) for i in range(h[12])]
    shstr = sections[h[13]]
    section_names = data[shstr[4]:shstr[4]+shstr[5]]
    def name(table, offset):
        return table[offset:table.index(b'\0', offset)].decode()
    result = []
    for s in sections:
        if s[1] != 4:  # SHT_RELA
            continue
        target = sections[s[7]]
        assert target[2] & 4, 'relocation must apply to executable code'
        symtab = sections[s[6]]
        strings = sections[symtab[6]]
        names = data[strings[4]:strings[4]+strings[5]]
        for off in range(s[4], s[4]+s[5], s[9]):
            place, info, addend = struct.unpack_from('<IIi', data, off)
            n = struct.unpack_from('<I', data, symtab[4]+(info >> 8)*symtab[9])[0]
            result.append((name(section_names, target[0]), place, info & 255, name(names, n), addend))
    return sorted(result)

def linked_bytes(path):
    data = path.read_bytes()
    h = struct.unpack_from('<16sHHIIIIIHHHHHH', data)
    assert h[0][:7] == b'\x7fELF\x01\x01\x01' and h[1] == 2 and h[2] == 243
    sections = [struct.unpack_from('<10I', data, h[6]+i*h[11]) for i in range(h[12])]
    code = [s for s in sections if s[3] == 0x901a and s[5] == 0x60 and s[2]&4]
    assert len(code) == 1
    symtab = [s for s in sections if s[1] == 2]; assert len(symtab) == 1
    s = symtab[0]; strings = sections[s[6]]; names = data[strings[4]:strings[4]+strings[5]]
    symbols = {}
    for off in range(s[4],s[4]+s[5],s[9]):
        n,v,size,info,other,sh = struct.unpack_from('<IIIBBH',data,off)
        if n: symbols[names[n:names.index(b'\0',n)].decode()] = (v,size,sh)
    for i,name in enumerate(NAMES):
        v,size,sh = symbols['tsl9_callback_table_'+name]
        assert v == ADDR[i] and size == ADDR[i+1]-ADDR[i] and sh != 0, name
    s = code[0]
    caller = symbols['probe_direct_caller']
    assert caller[0] == 0x8000 and caller[1] == 8 and caller[2] != 0
    caller_section = sections[caller[2]]
    assert caller_section[2] & 4
    offset = caller_section[4] + caller[0] - caller_section[3]
    auipc, jalr = struct.unpack_from('<II', data, offset)
    assert auipc & 0xfff == 0x97 and jalr & 0xfffff == 0x080e7
    hi = struct.unpack('<i', struct.pack('<I', auipc & 0xfffff000))[0]
    lo = struct.unpack('<i', struct.pack('<I', jalr & 0xfff00000))[0] >> 20
    assert (caller[0] + hi + lo) & 0xffffffff == symbols['tsl9_callback_table_entry_901a'][0]
    return data[s[4]:s[4]+s[5]]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ndk-bin',type=pathlib.Path,default=TOOLS); args=ap.parse_args()
    original = BIN.read_bytes()
    assert hashlib.sha256(original).hexdigest() == '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667', (str(BIN),len(original),hashlib.sha256(original).hexdigest())
    reference = original[0x901a-0x8000:0x907a-0x8000]
    assert hashlib.sha256(reference).hexdigest() == '1ca1876ac3f3458d2a170336f9d1598ee7dd62f359f802ceae6739d04fda437f'
    text = SOURCE.read_text(encoding='utf-8').split('/* Original 907A..9096 */')[0]
    assert not any(directive in text for directive in ('.byte', '.2byte', '.4byte', '.word', '.insn'))
    mutations = {
        'semantic': ('a4 = UINT32_C(15); LIVE;', 'a4 = UINT32_C(14); LIVE;'),
        'branch-target': ('R_RISCV_RVC_BRANCH,tsl9_callback_table_block_9070', 'R_RISCV_RVC_BRANCH,tsl9_callback_table_block_9066'),
        'branch-condition': ('c.beqz a5,.Lcallback_edge_902c', 'c.bnez a5,.Lcallback_edge_902c'),
    }
    for before, _ in mutations.values(): assert text.count(before) == 1
    expected_relocs = sorted([
        ('.text.tsl9_callback_table_block_9026', 6, 44, 'tsl9_callback_table_block_9070', 0),
        ('.text.tsl9_callback_table_block_902e', 20, 44, 'tsl9_callback_table_block_905a', 0),
        ('.text.tsl9_callback_table_block_9044', 10, 44, 'tsl9_callback_table_block_9058', 0),
        ('.text.tsl9_callback_table_block_9070', 2, 16, 'tsl9_callback_table_block_9026', 0),
        ('.text.tsl9_callback_table_block_9076', 2, 45, 'tsl9_callback_table_block_9066', 0),
    ])
    with tempfile.TemporaryDirectory() as tmp:
        d=pathlib.Path(tmp)
        script = 'SECTIONS {\n  .probe 0x8000 : { *(.text.probe) }\n  .text 0x901a : {\n' + ''.join('    KEEP(*(.text.tsl9_callback_table_'+n+'))\n' for n in NAMES) + '  }\n}\n'
        (d/'layout.ld').write_text(script)
        (d/'probe.S').write_text('.section .text.probe,"ax",@progbits\n.globl probe_direct_caller\n.type probe_direct_caller,@function\nprobe_direct_caller:\n.option push\n.option norelax\ncall tsl9_callback_table_entry_901a\n.option pop\n.size probe_direct_caller,.-probe_direct_caller\n')
        run([args.ndk_bin/'clang.exe',*FLAGS,'-c',d/'probe.S','-o',d/'probe.o'])
        assert object_relocations(d/'probe.o') == [('.text.probe', 0, 19, 'tsl9_callback_table_entry_901a', 0)]
        for mode in ('c','cpp'):
            for mutation in ('none', *mutations):
                src=d/'input.c'; src.write_text(text if mutation == 'none' else text.replace(*mutations[mutation]),encoding='utf-8')
                obj=d/'input.o'; elf=d/'linked.elf'
                language=['-x','c++','-std=c++17','-fno-exceptions','-fno-rtti'] if mode=='cpp' else ['-x','c','-std=c11']
                run([args.ndk_bin/'clang.exe',*FLAGS,*language,'-c',src,'-o',obj])
                relocs = object_relocations(obj)
                if mutation == 'branch-target':
                    assert relocs != expected_relocs, 'target mutation escaped relocation audit'
                else:
                    assert relocs == expected_relocs, (mutation, relocs)
                run([args.ndk_bin/'ld.lld.exe','--no-relax','-T',d/'layout.ld','-o',elf,d/'probe.o',obj])
                got=linked_bytes(elf)
                diffs=[hex(0x901a+i) for i,(a,b) in enumerate(zip(got,reference)) if a!=b]
                if mutation != 'none':
                    assert diffs, mutation+' mutation was not rejected'
                else:
                    assert not diffs, 'original-VA byte mismatch: '+str(diffs)
                print(mode, mutation, 'rejected' if diffs else 'original-VA exact match', 'differences:', diffs)
if __name__ == '__main__': main()
