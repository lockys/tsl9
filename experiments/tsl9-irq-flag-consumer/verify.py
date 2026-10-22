#!/usr/bin/env python3
"""Build/replay an offline ET_REL consumer with two intentionally OPEN JALs."""
import sys
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import struct
import subprocess

HERE = Path(__file__).resolve().parent
MODEL = 'experiments/tsl9-irq-flag-consumer'
ENTRY = 'tsl9_flag_consumer_entry_17002'
BODY = 'tsl9_flag_consumer_body'
PROVIDER = 'tsl9_receive_entry_16b0a'
SOURCE = MODEL + '/src/flag_consumer.c'
SOURCE_PIN = '9edf5f2571991062605863e88adf8028d4d54efc8d3e518c540026bd50b0ef12'
LINKER_PIN = 'f52c36c59ea09f93b7ce8eadc4e39d49dc1704ab4745202ef1fd102149344ba9'
PARSER = 'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py'
PARSER_PIN = '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
FIRMWARE = 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
IMAGE_PIN = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
ORIGINAL_PIN = 'dd6b0fa91982cf653657b71e2d2bfaf2d6349ccc12f2b31561483e40572b0c69'
NONCALL_PIN = 'c7401860f08f143e7fd39ca6c9d85b6a539aea9c813ddb13ed67441b0403ac25'
STDINT_PIN = '7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
TOOLS = {
    'clang': '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
    'ld.lld': 'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
    'llvm-objdump': 'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa',
}
ENTRY_IR_PIN = 'c4a974c968b62b83d5b03b3dfa49a01737e46158f91cfcf73fd3625555acce8d'
BODY_IR_PIN = {'c': '9a46e4f08bb1391536762550479cbab938431f295af2cb7e0541f42f15f494fa',
               'cpp': '7b5c32e78d9a600daa5e384ca9d13e345d7f3ea7bda81cd6e9c1186cfa671364'}
ORIGINAL = bytes.fromhex('411183c7811606c613f7170009cbf99b05452384f116eff03faf'
                         'a384011683c7811613f7270009cbf59b09452384f116eff09fad'
                         '23850116b24041018280')
SITES = [(0,2),(2,4),(6,2),(8,4),(12,2),(14,2),(16,2),(18,4),(22,4),(26,4),
         (30,4),(34,4),(38,2),(40,2),(42,2),(44,4),(48,4),(52,4),(56,2),(58,2),(60,2)]
ARTIFACTS = {'native.o', 'native.ll', 'native.d', 'COMPONENT-OPEN-CALLS.o',
             'compile.log', 'IR.log', 'combine.log', 'object.log', 'combined.log'}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return digest(path.read_bytes())


def sx(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def noncall(code):
    return code[:22] + code[26:48] + code[52:]


def trace(code, resolved=False):
    """Read typed operands only; never evaluate target instructions or MMIO."""
    need(len(code) == 62, 'Exact62B extent')
    word = lambda at: struct.unpack_from('<I', code, at)[0]
    half = lambda at: struct.unpack_from('<H', code, at)[0]

    def immediate(at, op, funct, rd, rs1, value):
        w = word(at)
        need((w & 127, w >> 12 & 7, w >> 7 & 31, w >> 15 & 31, sx(w >> 20, 12)) ==
             (op, funct, rd, rs1, value), 'Typed immediate/load at+' + str(at))

    def store(at, source, offset):
        w = word(at)
        need((w & 127, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31,
              sx((w >> 25 << 5) | (w >> 7 & 31), 12)) == (0x23, 0, 3, source, offset),
             'Typed SB8 currentGP at+' + str(at))

    def compressed(at, funct, rd, value):
        h = half(at)
        need((h & 3, h >> 13, h >> 7 & 31, sx((h >> 12 & 1) << 5 | (h >> 2 & 31), 6)) ==
             (1, funct, rd, value), 'Typed compressed SP/channel at+' + str(at))

    def branch(at, target):
        h = half(at)
        delta = sx(((h >> 12 & 1) << 8) | ((h >> 10 & 3) << 3) | ((h >> 5 & 3) << 6)
                   | ((h >> 3 & 3) << 1) | ((h >> 2 & 1) << 5), 9)
        need((h & 3, h >> 13, 8 + (h >> 7 & 7), at + delta) == (1, 6, 14, target),
             'Typed BEQZ A4 target at+' + str(at))

    def mask(at, value):
        h = half(at)
        need((h & 3, h >> 13, h >> 10 & 3, 8 + (h >> 7 & 7),
              sx((h >> 12 & 1) << 5 | (h >> 2 & 31), 6)) == (1, 4, 2, 15, value),
             'Typed compressed A5 clear mask at+' + str(at))

    compressed(0, 0, 2, -16)
    immediate(2, 3, 4, 15, 3, 360)
    h = half(6)
    need((h & 3, h >> 13, h >> 2 & 31, ((h >> 9 & 15) << 2) | ((h >> 7 & 3) << 6)) ==
         (2, 6, 1, 12), 'RA save12SP after first byte read')
    immediate(8, 0x13, 7, 14, 15, 1)
    branch(12, 30)
    mask(14, -2)
    compressed(16, 2, 10, 1)
    store(18, 15, 360)
    store(26, 0, 361)
    immediate(30, 3, 4, 15, 3, 360)
    immediate(34, 0x13, 7, 14, 15, 2)
    branch(38, 56)
    mask(40, -3)
    compressed(42, 2, 10, 2)
    store(44, 15, 360)
    store(52, 0, 362)
    h = half(56)
    need((h & 3, h >> 13, h >> 7 & 31,
          ((h >> 12 & 1) << 5) | ((h >> 4 & 7) << 2) | ((h >> 2 & 3) << 6)) ==
         (2, 2, 1, 12), 'Fresh RA reload12SP after possible calls')
    compressed(58, 0, 2, 16)
    need(half(60) == 0x8082, 'RET via freshly reloaded RA')
    calls = []
    for at in (22, 48):
        w = word(at)
        displacement = sx(((w >> 31) << 20) | ((w >> 21 & 1023) << 1)
                          | ((w >> 20 & 1) << 11) | ((w >> 12 & 255) << 12), 21)
        need((w & 127, w >> 7 & 31) == (0x6f, 1), 'Four-byte JAL RA at+' + str(at))
        if resolved:
            need(0x17002 + at + displacement == 0x16b0a, 'Original resolved JAL target16B0A')
        else:
            need(w == 0x000000ef, 'Open JAL raw word000000ef')
        calls.append(dict(offset=at, encoded_displacement=displacement,
                          resolved_target='0x16b0a' if resolved else None,
                          pending_relocation=not resolved,
                          original_continuation=hex(0x17002 + at + 4)))
    return dict(bytes=62, instructions=21, calls=calls,
                rows=[dict(offset=at, bytes=size, hex=code[at:at+size].hex()) for at,size in SITES],
                frame_bytes=16, prefix_order=['SP-16', 'LBU8 liveGP+360', 'SW32 RA,12SP'],
                exit_order=['LW32 RA,12SP', 'SP+16', 'RET'], branches=[[12,30],[38,56]],
                flag_byte_load_sites=2, flag_byte_store_sites=4, own_GP_writes=False,
                C_allocator_bank=['a0','a4','a5'], architectural_port_registers=['sp','ra'])


def flags(mode):
    need(mode in ('c', 'cpp'), 'Known language')
    return ['--target=riscv32-unknown-elf', '-march=rv32imac_zicsr_zifencei', '-mabi=ilp32',
            '-Oz', '-mllvm', '-enable-machine-outliner=never', '-ffreestanding', '-fno-builtin',
            '-fno-stack-protector', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
            '-mno-relax', '-ffunction-sections', '-fdata-sections', '-Wall', '-Wextra', '-Werror',
            '-x', 'c' if mode == 'c' else 'c++', '-std=c11' if mode == 'c' else '-std=c++17',
            *(['-fno-exceptions'] if mode == 'cpp' else []),
            *['-ffixed-x' + str(n) for n in range(1,32) if n not in {10,14,15}]]


def portable(value, root, tools, header):
    text = str(value).replace('\\', '/')
    for path, label in [(header.parent, '${CLANG_INCLUDE}'),
                        (tools['clang'].parent, '${LLVM_BIN}'), (root, '${PROJECT_ROOT}')]:
        prefix = path.as_posix()
        if text == prefix or text.startswith(prefix + '/'):
            return label + text[len(prefix):]
    return text


def portable_record(value):
    if isinstance(value, dict):
        for key, item in value.items():
            portable_record(key)
            portable_record(item)
    elif isinstance(value, list):
        for item in value:
            portable_record(item)
    elif isinstance(value, str):
        need(not re.search(r'(?i)([a-z]:[/\\]|/(?:users|home)/|\\\\)', value)
             and not value.startswith('/'), 'Portable receipt fields only')


def load(root, tool_dir):
    need(HERE == root / MODEL and sha(root / SOURCE) == SOURCE_PIN, 'Frozen current source')
    need(sha(HERE / 'component.ld') == LINKER_PIN, 'Frozen ET_REL-only linker')
    need(sha(root / PARSER) == PARSER_PIN, 'Frozen bounded ELF parser')
    tools = {name: (tool_dir / (name + ('.exe' if os.name == 'nt' else ''))).resolve()
             for name in TOOLS}
    need(all(sha(tools[n]) == pin for n,pin in TOOLS.items()), 'Pinned existing LLVM tools')
    header = tools['clang'].parent.parent / 'lib/clang/18/include/stdint.h'
    need(sha(header) == STDINT_PIN, 'Pinned compiler stdint resource')
    return tools, header, runpy.run_path(str(root / PARSER))['ELF']


def inputs(root, tools, header):
    files = [Path(__file__).resolve(), root / SOURCE, HERE / 'component.ld', root / PARSER,
             root / FIRMWARE, header, *tools.values()]
    return {portable(path, root, tools, header): sha(path) for path in sorted(files)}


def originals(root):
    image = (root / FIRMWARE).read_bytes()
    need(len(image) == 76800 and digest(image) == IMAGE_PIN, 'Pinned original full Runtime')
    code = image[0xf002:0xf040]
    need(code == ORIGINAL and digest(code) == ORIGINAL_PIN and digest(noncall(code)) == NONCALL_PIN,
         'Original complete62B and noncall54B')
    return trace(code, True)


def recipes(root, folder, mode, tools):
    common = [tools['clang'], *flags(mode)]
    return [('compile', [*common, '-c', '-MD', '-MF', folder / 'native.d', '-MT', 'native.o',
                         root / SOURCE, '-o', folder / 'native.o']),
            ('IR', [*common, '-S', '-emit-llvm', root / SOURCE, '-o', folder / 'native.ll']),
            ('combine', [tools['ld.lld'], '-r', '--no-relax', '-T', HERE / 'component.ld',
                         folder / 'native.o', '-o', folder / 'COMPONENT-OPEN-CALLS.o']),
            ('object', [tools['llvm-objdump'], '--mattr=+m,+a,+c,+zicsr,+zifencei', '-d', '-r', folder / 'native.o']),
            ('combined', [tools['llvm-objdump'], '--mattr=+m,+a,+c,+zicsr,+zifencei', '-d', '-r',
                          folder / 'COMPONENT-OPEN-CALLS.o'])]


def dependencies(root, folder, tools, header):
    target, separator, tail = (folder / 'native.d').read_text().replace('\\\n', ' ').partition(':')
    paths = {Path(re.sub(r'\\(.)', r'\1', item)).resolve() for item in re.findall(r'(?:\\.|[^\s])+', tail)}
    need(separator and target == 'native.o' and paths == {root / SOURCE, header}, 'Exact MD source/header closure')
    return {portable(p, root, tools, header): sha(p) for p in sorted(paths)}


def ir_bodies(text):
    found = re.findall(r'define[^\n]*@([^ (]+)\([^\n]*\{\n(.*?)\n}', text, re.S)
    need(len(found) == 2 and {name for name,_ in found} == {ENTRY,BODY}, 'Exactly two actual IR functions')
    result = {}
    for name, body in found:
        lines = []
        for line in body.splitlines():
            line = line.split(';', 1)[0].strip()
            if line:
                lines.append(re.sub(r' #\d+\b', '', re.sub(r', ![A-Za-z.]+ !\d+', '', line)))
        result[name] = '\n'.join(lines) + '\n'
    return result


def ir_contract(text, mode, full=True):
    bodies = ir_bodies(text)
    entry, body = bodies[ENTRY], bodies[BODY]
    expected_entry = (r'tail call void asm sideeffect "addi sp, sp, -16\0Albu a5, 360(gp)\0Asw ra, 12(sp)\0A", ""()'
                      + '\nunreachable\n')
    need(entry == expected_entry, 'Exact architectural entry8B order in IR')
    gp = 'tail call ' + ('noundef ' if mode == 'cpp' else '') + 'i32 asm sideeffect "", "={x3},~{memory}"()'
    need(body.count(gp) == 5, 'Five distinct liveGP imports')
    need(body.count('load volatile i8,') == 1 and body.count('store volatile i8 ') == 4,
         'One fresh body byte read and four volatile byte stores')
    anchors = [
        '%1 = tail call i32 asm sideeffect "", "={x15},~{memory}"()',
        '%2 = and i32 %1, 1', 'br i1 %5, label %21, label %6',
        '%15 = add i32 %14, 360', 'store volatile i8 %13, ptr %16, align 1',
        '%19 = add i32 %18, 361', 'store volatile i8 0, ptr %20, align 1',
        '%23 = add i32 %22, 360', '%25 = load volatile i8, ptr %24, align 1',
        '%27 = and i32 %26, 2', 'br i1 %30, label %46, label %31',
        '%40 = add i32 %39, 360', 'store volatile i8 %38, ptr %41, align 1',
        '%44 = add i32 %43, 362', 'store volatile i8 0, ptr %45, align 1',
        '%14 = ' + gp, '%18 = ' + gp, '%22 = ' + gp, '%39 = ' + gp, '%43 = ' + gp,
    ]
    need(all(anchor in body for anchor in anchors), 'Fresh GP byte dataflow and separate branch CFG')
    call = (r'tail call i32 asm sideeffect "jal ra, tsl9_receive_entry_16b0a\0A", '
            r'"={x10},{x10},~{x14},~{x15},~{memory}"')
    need(body.count(call) == 2 and (call + '(i32 %12)') in body and (call + '(i32 %37)') in body,
         'Two private JAL ports with opaque A0 result and only declared scratch bank')
    need('(i32 %4, i32 %9, i32 1)' in body and '(i32 %29, i32 %34, i32 2)' in body,
         'Channel A0 established only on taken branches')
    epilogue = (r'tail call void asm sideeffect "lw ra, 12(sp)\0Aaddi sp, sp, 16\0Aret\0A", "~{memory}"()'
                + '\nunreachable\n')
    need(body.endswith(epilogue), 'Fresh RA slot reload, SP restore, RET; no A0 normalization')
    need('alloca ' not in body and not re.search(r'\bcall\b[^\n]*@[A-Za-z_]', body), 'No second C frame or ordinary helper')
    if full:
        need(digest(entry.encode()) == ENTRY_IR_PIN and digest(body.encode()) == BODY_IR_PIN[mode],
             'Complete mode-specific entry/body SSA and CFG hash')
    return dict(entry_sha256=digest(entry.encode()), body_sha256=digest(body.encode()),
                body_lines=len(body.splitlines()), live_GP_imports=5,
                C_return_ABI=False, source_body_exit='architectural RET port followed by unreachable',
                A0_residue='entry A0 if no call; opaque returned A0 from last taken JAL otherwise')


def section_contract(elf, combined):
    fields = ('name','type','flags','address','size','link','info','alignment','entry_size')
    if combined:
        expected = [('',0,0,0,0,0,0,0,0),('.consumer',1,6,0,62,0,0,2,0),
                    ('.text',1,6,0,0,0,0,2,0),('.rela.consumer',4,64,0,24,5,1,4,12),
                    ('.llvm_addrsig',0x6fff4c03,0x80000000,0,2,0,0,1,0),
                    ('.symtab',2,0,0,176,7,8,4,16),('.shstrtab',3,0,0,72,0,0,1,0),
                    ('.strtab',3,0,0,112,0,0,1,0)]
    else:
        expected = [('',0,0,0,0,0,0,0,0),('.strtab',3,0,0,213,0,0,1,0),('.text',1,6,0,0,0,0,2,0),
                    ('.text.'+ENTRY,1,6,0,8,0,0,2,0),('.text.'+BODY,1,6,0,54,0,0,2,0),
                    ('.rela.text.'+BODY,4,64,0,24,10,4,4,12),('.comment',1,48,0,159,0,0,1,1),
                    ('.note.GNU-stack',1,0,0,0,0,0,1,0),('.riscv.attributes',0x70000003,0,0,64,0,0,1,0),
                    ('.llvm_addrsig',0x6fff4c03,0x80000000,0,2,10,0,1,0),('.symtab',2,0,0,144,1,6,4,16)]
    actual = [tuple(s[k] for k in fields) for s in elf.sections]
    need(actual == expected, 'Exact ET_REL section inventory, metadata and zero addresses')
    return [dict(zip(fields,row)) for row in actual]


def symbol_contract(elf, combined):
    rows = [('',0,0,0,0,0),('flag_consumer.c',0,0,4,0,65521),
            ('$x.0',0,0,0,0,1 if combined else 3),('$x.1',8 if combined else 0,0,0,0,1 if combined else 4)]
    if combined:
        rows += [('$d.3',0,0,0,0,65521),('',0,0,3,0,1),('',0,0,3,0,2),('',0,0,3,0,4)]
    else:
        rows += [('$d.2',0,0,0,0,6),('$d.3',0,0,0,0,8)]
    rows += [(ENTRY,0,8,18,0,1 if combined else 3),(BODY,8 if combined else 0,54,18,0,1 if combined else 4),
             (PROVIDER,0,0,16,0,0)]
    fields = ('name','value','size','info','other','index')
    expected = [dict(zip(fields,row)) for row in rows]
    need(elf.symbols == expected, 'Exact two FUNCs and genuine sole UND; no ABS or alias provider')
    return expected


def elf_contract(elf, combined, compare_hash=True):
    header = struct.unpack_from('<16sHHIIIIIHHHHHH', elf.raw)
    need(elf.kind == 1 and elf.flags == 1 and header[4] == 0 and header[5] == header[9] == header[10] == 0,
         'ET_REL only; no executable entry or program headers')
    need(header[3] == 1 and header[8] == 52 and header[11] == 40, 'ELF header sizes and version')
    sections = section_contract(elf, combined)
    symbols = symbol_contract(elf, combined)
    functions = {s['name']:s for s in symbols if s['info'] == 18}
    entry = elf.function_bytes(functions[ENTRY])
    body = elf.function_bytes(functions[BODY])
    code = entry + body
    if combined:
        need(elf.data(elf.byname['.consumer']) == code and functions[BODY]['value'] == 8,
             'Actual same-section fall-through adjacency entry8 plus body54')
    relocs = [dict(owner=r['owner'],offset=r['offset'],type=r['type'],addend=r['addend'],symbol=r['symbol'])
              for r in elf.relocations]
    expected = [dict(owner='.consumer' if combined else '.text.'+BODY,
                     offset=at if combined else at-8,type=17,addend=0,symbol=symbols[-1]) for at in (22,48)]
    need(relocs == expected, 'Exactly two open R_RISCV_JAL17 sites, target UND and zero addends')
    observed = trace(code)
    if compare_hash:
        need(noncall(code) == noncall(ORIGINAL) and digest(noncall(code)) == NONCALL_PIN,
             'Complete original54B outside only two explicit4B JAL windows')
    return dict(file_kind='ET_REL',combined=combined,entry_meaning='none: relocatable component',
                defined_functions=[functions[ENTRY],functions[BODY]],
                sections=sections,symbols=symbols,relocations=relocs,allocated_bytes=62,
                UND_providers=[PROVIDER],ABS_providers=[],
                local_ABS_metadata=[s for s in symbols if s['index']==65521],
                code_sha256=digest(code),noncall54_sha256=digest(noncall(code)),trace=observed)


class MemoryFile:
    def __init__(self, data):
        self.data = data

    def read_bytes(self):
        return self.data


def controls(reader, native, combined, ir, mode):
    results = []
    code = combined.data(combined.byname['.consumer'])

    def reject(label, operation, category):
        try:
            operation()
        except ValueError as error:
            results.append(dict(label=label,category=category,rejected_by=str(error),full_hash_used=False))
        else:
            raise ValueError('Negative control accepted: '+label)

    mutations = [('SP-allocation',0,0x20),('first-LBU-width',3,0x10),('RA-save-slot',7,0x02),
                 ('first-mask',10,0x10),('first-branch-polarity',13,0x20),('clear-bit1',14,0x04),
                 ('channel1',16,0x04),('first-SB-width',19,0x10),('JAL-not-RA',22,0x80),
                 ('clear361-offset',28,0x10),('second-fresh-GP-source',32,0x08),
                 ('second-branch-target',38,0x04),('clear-bit2',40,0x04),('channel2',42,0x04),
                 ('nonzero-open-JAL-immediate',51,0x01),('clear362-offset',54,0x10),
                 ('fresh-RA-reload-slot',56,0x10),('SP-restore',58,0x20),('RET-other-register',60,0x80)]
    for label,offset,mask in mutations:
        changed=bytearray(code);changed[offset]^=mask
        reject(label,lambda changed=changed:trace(bytes(changed)),'typed-raw')
    changed = code[:2]+code[6:8]+code[2:6]+code[8:]
    reject('prefix-read-before-save-order',lambda:trace(changed),'typed-raw')

    def changed_elf(offset, fmt, value):
        raw = bytearray(combined.raw)
        struct.pack_into(fmt,raw,offset,value)
        return reader(MemoryFile(bytes(raw)))

    rela = combined.byname['.rela.consumer']['offset']
    last_symbol = combined.byname['.symtab']['offset'] + 10*16
    section_table = struct.unpack_from('<I',combined.raw,32)[0]
    for label,offset,fmt,value in [('reloc-type',rela+4,'<I',(10<<8)|18),
                                   ('reloc-addend',rela+8,'<i',4),('reloc-site',rela,'<I',23),
                                   ('fake-ABS-provider',last_symbol+14,'<H',65521),
                                   ('broken-body-adjacency',combined.byname['.symtab']['offset']+9*16+4,'<I',10),
                                   ('false-nominal-VA',section_table+40+12,'<I',0x17002)]:
        reject(label,lambda offset=offset,fmt=fmt,value=value:
               elf_contract(changed_elf(offset,fmt,value),True,False),'actual-ELF-metadata')
    mutations = [('GP-port','={x3},~{memory}','={x4},~{memory}'),
                 ('fresh-GP-after-first-call','%18 = tail call','%18 = noncall'),
                 ('reuse-first-flag','%25 = load volatile i8, ptr %24, align 1','%25 = trunc i32 %1 to i8'),
                 ('second-branch-CFG','br i1 %30, label %46, label %31','br i1 %30, label %31, label %46'),
                 ('byte-store-width','store volatile i8 %13','store volatile i16 %13'),
                 ('postcall-clear361','%19 = add i32 %18, 361','%19 = add i32 %18, 360'),
                 ('return-slot',r'lw ra, 12(sp)\0A',r'lw ra, 8(sp)\0A'),
                 ('entry-read-order',r'addi sp, sp, -16\0Albu a5, 360(gp)\0Asw ra, 12(sp)',
                  r'addi sp, sp, -16\0Asw ra, 12(sp)\0Albu a5, 360(gp)'),
                 ('foreign-callee','jal ra, tsl9_receive_entry_16b0a','jal ra, invented_provider'),
                 ('A0-normalized-at-return',r'lw ra, 12(sp)\0A',r'li a0, 0\0Alw ra, 12(sp)\0A')]
    for label,old,new in mutations:
        need(old in ir,'Actual IR mutation anchor')
        reject(label,lambda old=old,new=new:ir_contract(ir.replace(old,new,1),mode,False),'IR-finite-gates')
    for label,old,new in [('full-SSA-store-value','%13 = trunc i32 %11 to i8','%13 = trunc i32 %12 to i8'),
                          ('full-SSA-clear-dataflow','%33 = and i32 %32, -3','%33 = and i32 %32, -4')]:
        changed=ir.replace(old,new,1)
        ir_contract(changed,mode,False)
        try:
            ir_contract(changed,mode,True)
        except ValueError as error:
            need(str(error)=='Complete mode-specific entry/body SSA and CFG hash','Full-IR hash rejection gate')
            results.append(dict(label=label,category='full-IR-SSA-hash',rejected_by=str(error),full_hash_used=True))
        else:
            raise ValueError('Whole SSA negative accepted')
    need(len(results)==38,'Complete38 negative-control set')
    return results


def objdump_contract(log, elf, combined):
    sections = {};current=None
    for line in log.read_text().splitlines():
        heading=re.match(r'Disassembly of section (.+):',line)
        if heading:current=heading[1]
        match=re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([^\s]+)',line)
        if match:
            need(match[3] not in ('<unknown>','.word','.2byte'),'Actual LLVM instruction decoding')
            sections.setdefault(current,[]).append((int(match[1],16),bytes.fromhex(match[2])))
    code=elf.data(elf.byname['.consumer']) if combined else (elf.data(elf.byname['.text.'+ENTRY])+elf.data(elf.byname['.text.'+BODY]))
    expected={'.consumer':[(at,code[at:at+size]) for at,size in SITES]} if combined else {
        '.text.'+ENTRY:[(at,code[at:at+size]) for at,size in SITES if at<8],
        '.text.'+BODY:[(at-8,code[at:at+size]) for at,size in SITES if at>=8]}
    need(sections==expected,'Complete21 objdump addresses/widths/bytes agree with ELF')
    return dict(instructions=sum(len(rows) for rows in sections.values()),bytes=62)


def inventory(folder):
    need(all(p.is_file() for p in folder.iterdir()),'No unrecorded artifact subdirectories')
    files={p.name:sha(p) for p in sorted(folder.iterdir()) if p.name!='verification.json'}
    need(set(files)==ARTIFACTS,'Exact nine-artifact inventory including raw logs')
    return files


def record(root,folder,mode,tools,header,reader):
    before=inputs(root,tools,header)
    original=originals(root)
    deps=dependencies(root,folder,tools,header)
    commands=[dict(label=label,argv=[portable(x,root,tools,header) for x in argv],exit=0,
                   log_sha256=sha(folder/(label+'.log'))) for label,argv in recipes(root,folder,mode,tools)]
    need(all((folder/(name+'.log')).read_bytes()==b'' for name in ('compile','IR','combine')),
         'Warning-free compiler, IR and partial-link logs')
    native=reader(folder/'native.o');combined=reader(folder/'COMPONENT-OPEN-CALLS.o')
    ir=(folder/'native.ll').read_text(encoding='utf-8')
    elf_facts=[elf_contract(native,False),elf_contract(combined,True)]
    ir_facts=ir_contract(ir,mode)
    negative=controls(reader,native,combined,ir,mode)
    disassembly=[objdump_contract(folder/'object.log',native,False),
                 objdump_contract(folder/'combined.log',combined,True)]
    after=inputs(root,tools,header)
    need(before==after,'Inputs unchanged through full verification')
    result=dict(passed=True,actual_ELFs=2,ELFs=elf_facts,IR=ir_facts,objdump=disassembly,
                original62_sha256=ORIGINAL_PIN,noncall54_sha256=NONCALL_PIN,
                full62_equal_to_resolved_original=False,whole_firmware_equivalence=False,
                emitted_nominal_VA=None,open_JAL_sites=[22,48],open_provider=PROVIDER,
                provider_implemented=False,firmware_ready=False,
                A0_residue=['No call: entry live A0 unchanged.','First call only: opaque first returned A0.',
                            'Second call taken: opaque second returned A0.'],
                limitations=['Only a relocatable component; no executable output or physical placement.',
                             'Two JAL relocations intentionally remain unresolved to one genuine UND provider.',
                             'Provider GP/SP/register effects, full IRQ/fault context and whole firmware are unproved.'],
                target_execution=False,ISA_emulation=False,MMIO_execution=False,hardware=False,network=False,BIN_generated=False)
    value=dict(schema='TSL9-flag-consumer-open-component-v1',mode=mode,
               firmware='${PROJECT_ROOT}/'+FIRMWARE,inputs_before=before,inputs_after=after,
               compiler_dependencies=deps,commands=commands,original_resolved_trace=original,
               negative_controls=negative,result=result,artifacts=inventory(folder))
    portable_record(value)
    return value


def replay(root,receipt,tools,header,reader):
    need(receipt.name=='verification.json' and receipt.parent.is_relative_to(HERE/'build')
         and receipt.parent.name in ('c','cpp'),'Owned replay receipt')
    raw=receipt.read_bytes()
    need(b'\r' not in raw,'Canonical LF receipt; preserve any historical raw records separately')
    saved=json.loads(raw)
    actual=record(root,receipt.parent,receipt.parent.name,tools,header,reader)
    need(actual==saved,'Complete read-only reconstructed record equality')
    return actual


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--tool-dir',type=Path,default=os.environ.get('TSL9_LLVM_BIN'))
    parser.add_argument('--build-root',type=Path)
    parser.add_argument('--replay',type=Path)
    parser.add_argument('--require-firmware-ready',action='store_true')
    args=parser.parse_args();root=args.project_root.resolve()
    need(args.tool_dir is not None,'Set TSL9_LLVM_BIN or explicit existing --tool-dir')
    tools,header,reader=load(root,Path(args.tool_dir).resolve())
    need((args.build_root is None)!=(args.replay is None),'Choose new build or read-only replay')
    if args.replay:
        value=replay(root,args.replay.resolve(),tools,header,reader)
        need(not args.require_firmware_ready,'OPEN JAL provider and complete firmware remain unproved')
        print(json.dumps(dict(passed=True,read_only_replay=True,actual_ELFs=2,negative_controls=len(value['negative_controls']),
                              firmware_ready=False,receipt_sha256=sha(args.replay.resolve()))))
        return
    need(not args.require_firmware_ready,'OPEN JAL provider and complete firmware remain unproved')
    out=args.build_root.resolve()
    need(out.is_relative_to(HERE/'build') and not out.exists(),'New owned build directory required')
    frozen=inputs(root,tools,header);originals(root);out.mkdir(parents=True)
    receipts=[]
    for mode in ('c','cpp'):
        folder=out/mode;folder.mkdir()
        for label,argv in recipes(root,folder,mode,tools):
            actual=subprocess.run([str(x) for x in argv],cwd=root,capture_output=True,timeout=120)
            (folder/(label+'.log')).write_bytes(actual.stdout+actual.stderr)
            need(actual.returncode==0,'Local compiler/static-reader command failed; inspect '+label+'.log')
            need(inputs(root,tools,header)==frozen,'Pre/post inputs unchanged for every actual recipe')
        value=record(root,folder,mode,tools,header,reader)
        need(value['inputs_before']==value['inputs_after']==frozen,'All build inputs unchanged')
        receipt=folder/'verification.json';receipt.write_bytes((json.dumps(value,indent=2)+'\n').encode('utf-8'))
        replay(root,receipt,tools,header,reader)
        receipts.append(dict(mode=mode,path=portable(receipt,root,tools,header),sha256=sha(receipt)))
    need(inputs(root,tools,header)==frozen,'Inputs unchanged across both language builds')
    need(all((out/'c'/name).read_bytes()==(out/'cpp'/name).read_bytes()
             for name in ('native.o','COMPONENT-OPEN-CALLS.o')),'C/C++ complete ELF byte equality')
    print(json.dumps(dict(passed=True,actual_ELFs=4,negative_controls_per_mode=38,receipts=receipts,
                          firmware_ready=False,open_JALs_per_object=2,target_execution=False,BIN_generated=False)))


if __name__=='__main__':
    try:
        main()
    except ValueError as error:
        print(json.dumps(dict(passed=False,error=str(error))))
        sys.exit(1)
