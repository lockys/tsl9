#!/usr/bin/env python3
"""Build/replay a single offline IRQ leaf. Never executes target code or emits BIN."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy
import struct
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODEL = 'experiments/tsl9-irq-flag-leaf'
SYMBOL = 'tsl9_irq_flag_leaf_16fb6'
SOURCE_SHA = 'a6c859e8e8a31e507bec11755aa147c622cc27ff0d1bc2606d76b9ce373d146e'
FW = 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
FW_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
CODE_SHA = '034c35bc979f6b1385f135ad466d7303c31429d9323484a6290314885ad26f85'
PARSER = 'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py'
PARSER_SHA = '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
STDINT_SHA = '7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
TOOLS = {
    'clang': '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
    'ld.lld': 'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
    'llvm-objdump': 'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa',
}
IR_SHA = {'c': 'ba8e073b0fb175368acc929abdfeeb4d655d5299cd28e216d527017ac75b089f',
          'cpp': '93eb0570f873516b591f96ac5d0833bcd0403021fb04459870b2234cb0ee7582'}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return digest(path.read_bytes())


def sx(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def source_contract(code):
    """Finite raw operand reader for exactly21 source instructions; no execution."""
    need(len(code) == 76, 'Exact original76B extent')
    rows = []
    for start, mask, flag in [(0, 64, 1), (36, 128, 2)]:
        word = lambda offset: struct.unpack_from('<I', code, start + offset)[0]
        def imm(offset, op, funct, rd, rs1, value):
            w = word(offset)
            need((w & 127, w >> 12 & 7, w >> 7 & 31, w >> 15 & 31, sx(w >> 20, 12)) ==
                 (op, funct, rd, rs1, value), 'Original typed immediate/load operand at+' + str(start + offset))
        w = word(0)
        need((w & 127, w >> 7 & 31, w & 0xfffff000) == (0x37, 15, 0x40010000),
             'Repeated original page-base LUI')
        imm(4, 3, 2, 14, 15, 1044)
        imm(8, 0x13, 0, 15, 15, 1024)
        imm(12, 0x13, 7, 14, 14, mask)
        h = struct.unpack_from('<H', code, start + 16)[0]
        displacement = sx(((h >> 12 & 1) << 8) | ((h >> 10 & 3) << 3) |
                          ((h >> 5 & 3) << 6) | ((h >> 3 & 3) << 1) | ((h >> 2 & 1) << 5), 9)
        need((h & 3, h >> 13, 8 + (h >> 7 & 7), start + 16 + displacement) ==
             (1, 6, 14, 36 if start == 0 else 72), 'Original BEQZ A4 target and polarity')
        imm(18, 0x13, 0, 14, 0, mask)
        h = struct.unpack_from('<H', code, start + 22)[0]
        offset = ((h >> 10 & 7) << 3) | ((h >> 6 & 1) << 2) | ((h >> 5 & 1) << 6)
        need((h & 3, h >> 13, 8 + (h >> 7 & 7), 8 + (h >> 2 & 7), offset) ==
             (0, 6, 15, 14, 20), 'Original compressed SW32 A4,20(A5)')
        imm(24, 3, 4, 15, 3, 360)
        imm(28, 0x13, 6, 15, 15, flag)
        w = word(32)
        offset = sx(((w >> 25) << 5) | (w >> 7 & 31), 12)
        need((w & 127, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31, offset) ==
             (0x23, 0, 3, 15, 360), 'Original SB8 A5,360(GP)')
        for offset, size in [(0,4),(4,4),(8,4),(12,4),(16,2),(18,4),(22,2),(24,4),(28,4),(32,4)]:
            rows.append(dict(offset=start + offset, bytes=size,
                             raw=code[start + offset:start + offset + size].hex(' ')))
    need(code[72:] == bytes.fromhex('73 00 20 30'), 'Original final MRET; no RET substitute')
    rows.append(dict(offset=72, bytes=4, raw=code[72:].hex(' ')))
    return dict(bytes=76, instructions=21, rows=rows, branches=[[16,36],[52,72]],
                own_written_GPRs=[14,15], SP_GP_RA_writes=False, calls=0,
                status_address='0x40010414', flag_address='live GP+360',
                READ32_sites=2, WRITE32_sites=2, READ8_sites=2, WRITE8_sites=2)


def normalized(ir):
    m = re.search(r'define[^\n]*@' + SYMBOL + r'\([^\n]*\{\n(.*?)\n}', ir, re.S)
    need(m, 'Genuine compiled IR definition')
    lines = []
    for line in m[1].splitlines():
        line = line.split(';')[0].strip()
        if line:
            lines.append(re.sub(r' #\d+\b', '', re.sub(r', ![A-Za-z.]+ !\d+', '', line)))
    return '\n'.join(lines) + '\n'


def ir_gate(ir, mode, full_hash=True):
    body = normalized(ir)
    need('alloca ' not in body and '@llvm.lifetime' not in body, 'No C frame or lifetime helper')
    for kind in ('load volatile i32', 'load volatile i8', 'store volatile i32', 'store volatile i8'):
        need(body.count(kind) == 2, 'Two distinct volatile sites: ' + kind)
    gp = 'tail call ' + ('noundef ' if mode == 'cpp' else '') + 'i32 asm sideeffect "", "={x3},~{memory}"()'
    need(body.count(gp) == 2, 'Exactly two live-GP imports; C++ noundef retained')
    anchors = [
        '%4 = load volatile i32, ptr %3, align 4',
        '%37 = load volatile i32, ptr %36, align 4',
        '%12 = and i32 %11, 64', '%45 = and i32 %44, 128',
        'br i1 %15, label %33, label %16', 'br i1 %49, label %66, label %50',
        '%26 = load volatile i8, ptr %25, align 1', '%59 = load volatile i8, ptr %58, align 1',
        'store volatile i8 %32, ptr %25, align 1', 'store volatile i8 %65, ptr %58, align 1',
        '"{x14},{x15},~{memory}"(i32 %67, i32 %68)',
    ]
    need(all(x in body for x in anchors), 'Fresh reads, byte widths, masks, CFG and output-bank dataflow')
    need(body.splitlines()[-2:] == [r'tail call void asm sideeffect "mret\0A", "~{memory}"()', 'unreachable'],
         'Only architectural MRET exit')
    need(not re.search(r'\bcall\b[^\n]*@[A-Za-z_]', body), 'No ordinary call or compiler helper')
    if full_hash:
        need(digest(body.encode()) == IR_SHA[mode], 'Whole mode-specific SSA/CFG/port IR')
    return dict(normalized_sha256=IR_SHA[mode], mode=mode, cpp_noundef_GP_ports=(mode == 'cpp'),
                distinct_volatile_sites_per_kind=2, second_frame=False, whole_body_checked=True)


def flags(mode):
    return ['--target=riscv32-unknown-elf', '-march=rv32imac_zicsr', '-mabi=ilp32', '-Oz',
            '-mllvm', '-enable-machine-outliner=never', '-ffreestanding', '-fno-builtin',
            '-fno-stack-protector', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
            '-mno-relax', '-ffunction-sections', '-fdata-sections', '-Wall', '-Wextra', '-Werror',
            *['-ffixed-x' + str(n) for n in range(1,32) if n not in {14,15}],
            '-x', 'c' if mode == 'c' else 'c++', '-std=c11' if mode == 'c' else '-std=c++17',
            *(['-fno-exceptions'] if mode == 'cpp' else [])]


def load(root, tool_dir):
    need(HERE == root / MODEL and sha(HERE / 'src/irq_flag.c') == SOURCE_SHA, 'Frozen canonical C source')
    need(sha(root / PARSER) == PARSER_SHA and sha(root / FW) == FW_SHA, 'Existing ELF reader and immutable firmware')
    tools = {name:tool_dir / (name + ('.exe' if sys.platform == 'win32' else '')) for name in TOOLS}
    need(all(sha(tools[n]) == h for n,h in TOOLS.items()), 'Pinned existing LLVM tools')
    header = tools['clang'].parent.parent / 'lib/clang/18/include/stdint.h'
    need(sha(header) == STDINT_SHA, 'Pinned compiler stdint header')
    return tools, header


def portable(value, root, tools, header):
    text = str(value).replace('\\','/')
    for path, label in [(header.parent, '${CLANG_INCLUDE}'),(tools['clang'].parent, '${LLVM_BIN}'),(root, '${PROJECT_ROOT}')]:
        base = path.as_posix()
        if text == base or text.startswith(base + '/'):
            return label + text[len(base):]
    return text


def inputs(root, tools, header):
    files = {Path(__file__).resolve(), HERE/'component.ld', HERE/'src/irq_flag.c', root/PARSER, root/FW, header, *tools.values()}
    return {portable(p,root,tools,header):sha(p) for p in sorted(files)}


def recipes(folder, mode, tools):
    common = [tools['clang'], *flags(mode)]
    obj, elf = folder/'native.o', folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf'
    return [('compile',[*common,'-c','-MD','-MF',folder/'native.d','-MT','native.o',HERE/'src/irq_flag.c','-o',obj]),
            ('IR',[*common,'-S','-emit-llvm',HERE/'src/irq_flag.c','-o',folder/'native.ll']),
            ('link',[tools['ld.lld'],'--no-relax','-T',HERE/'component.ld',obj,'-o',elf]),
            ('object',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr','-d','-r',obj]),
            ('linked',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr','-d','-r',elf])]


def commands(folder, mode, root, tools, header):
    return [dict(label=k,argv=[portable(x,root,tools,header) for x in argv],exit=0,
                 log_sha256=sha(folder/(k+'.log'))) for k,argv in recipes(folder,mode,tools)]


def inspect_elf(path, log, root, original, linked):
    E = runpy.run_path(str(root/PARSER))['ELF']
    elf = E(path)
    need(elf.kind == (2 if linked else 1) and elf.flags == 1, 'RV32 RVC ELF kind and flags')
    funcs = [s for s in elf.symbols if s['info']&15 == 2 and s['size']]
    need(len(funcs) == 1 and funcs[0]['name'] == SYMBOL and funcs[0]['size'] == 76 and funcs[0]['info']>>4 == 1,
         'Exactly one genuine76B global FUNC')
    globals_ = [s for s in elf.symbols if s['name'] and s['info']>>4 in (1,2)]
    need(len(globals_) == 1 and globals_[0] == funcs[0], 'No UND/ABS/alias/dummy provider definitions')
    need(not elf.relocations, 'No unresolved or residual relocations')
    alloc = [s for s in elf.sections if s['flags']&2 and s['size']]
    need(len(alloc) == 1 and (alloc[0]['type'],alloc[0]['flags'],alloc[0]['size'],alloc[0]['alignment']) == (1,6,76,2),
         'Only76 AX bytes; no padding/data/BSS/unwind/carrier')
    section = alloc[0]
    need(section['name'] == ('.irq' if linked else '.text.'+SYMBOL), 'Declared code section only')
    need(funcs[0]['value'] == section['address'] == (0x16fb6 if linked else 0), 'Real entry and section placement')
    if linked:
        need(struct.unpack_from('<I',elf.raw,24)[0] == 0x16fb6, 'ELF entry points to actual IRQ leaf')
    code = elf.function_bytes(funcs[0])
    need(code == elf.data(section) == original and digest(code) == CODE_SHA, 'Whole object/linked76B equals actual original')
    contract = source_contract(code)
    rows, current = [], None
    for line in log.read_text(encoding='utf-8').splitlines():
        heading = re.match(r'Disassembly of section (.+):',line)
        if heading:
            current = heading[1]
        match = re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([^\s]+)\s*(.*)',line)
        if match:
            need(current == section['name'] and match[3] not in ('<unknown>','.word','.2byte'), 'Actual LLVM instruction owner/decoding')
            rows.append(dict(offset=int(match[1],16)-section['address'],bytes=len(bytes.fromhex(match[2])),
                             raw=bytes.fromhex(match[2]).hex(' ')))
    need(rows == contract['rows'], 'All21 LLVM addresses/widths/raw bytes match complete ELF/source extent')
    return dict(file=path.name,linked=linked,code_sha256=digest(code),bytes=76,instructions=21,
                symbol=SYMBOL,value=funcs[0]['value'],UND_providers=0,ABS_providers=0,relocations=0,
                local_ABS_metadata=[s for s in elf.symbols if s['index'] == 65521 and s['info']>>4 == 0],
                section={k:section[k] for k in ('name','type','flags','address','size','alignment')}), contract


def negatives(code, ir, mode):
    results = []
    for label, at, mask in [('page-base',3,1),('first-read-offset',6,16),('base-adjust',11,1),
                            ('bit64',15,1),('first-branch-polarity',17,32),('word-store-width',23,32),
                            ('flag-load-register',24,128),('flag-GP-offset',26,16),('OR1',30,16),
                            ('second-fresh-offset',42,16),('bit128',51,1),('second-branch-target',52,4),
                            ('OR2',66,16),('byte-store-width',69,32),('MRET',72,20)]:
        changed = bytearray(code); changed[at] ^= mask
        try:
            source_contract(bytes(changed))
        except ValueError as exc:
            results.append(dict(label=label,rejected_by=str(exc),whole_code_hash_used=False))
        else:
            raise ValueError('Raw negative escaped: '+label)
    for label, old, new in [('fresh-second-read','%37 = load volatile i32, ptr %36, align 4','%37 = add i32 %4, 0'),
                            ('volatile-read','%4 = load volatile i32','%4 = load i32'),
                            ('second-mask','%45 = and i32 %44, 128','%45 = and i32 %44, 64'),
                            ('GP-port','={x3},~{memory}','={x4},~{memory}'),
                            ('byte-write','store volatile i8 %65','store volatile i32 %65'),
                            ('branch-CFG','br i1 %49, label %66, label %50','br i1 %49, label %50, label %66'),
                            ('output-bank','{x14},{x15},~{memory}','{x15},{x14},~{memory}'),
                            ('MRET-port',r'mret\0A',r'ret\0A')]:
        need(old in ir, 'Actual IR negative anchor')
        try:
            ir_gate(ir.replace(old,new,1),mode,False)
        except ValueError as exc:
            results.append(dict(label=label,rejected_by=str(exc),whole_IR_hash_used=False))
        else:
            raise ValueError('IR negative escaped: '+label)
    need(len(results) == 23, 'Complete finite negative-control set')
    return results


def inventory(folder):
    need(all(p.is_file() for p in folder.iterdir()), 'No unaudited artifact subdirectories')
    return {p.name:sha(p) for p in sorted(folder.iterdir()) if p.name != 'verification.json'}


def inspect(root, folder, tools, header):
    produced = json.loads((folder/'build.json').read_bytes())
    need(produced['schema'] == 'TSL9-IRQ-flag-leaf-build-v1' and produced['mode'] in ('c','cpp'), 'Known build and language')
    mode = produced['mode']
    need(produced['inputs'] == inputs(root,tools,header) and produced['commands'] == commands(folder,mode,root,tools,header),
         'Complete unchanged source/header/tools and exact successful command/log recipes')
    expected = {'native.o','native.ll','native.d','COMPONENT-ONLY-NOT-FIRMWARE.elf','build.json',
                'compile.log','IR.log','link.log','object.log','linked.log'}
    need(set(inventory(folder)) == expected, 'Complete producer artifact inventory')
    target, separator, tail = (folder/'native.d').read_text().replace('\\\n',' ').partition(':')
    deps = {Path(re.sub(r'\\(.)',r'\1',x)).resolve() for x in re.findall(r'(?:\\.|[^\s])+',tail)}
    need(separator and target == 'native.o' and deps == {HERE/'src/irq_flag.c',header}, 'Exact actual MD source/header closure')
    image = (root/FW).read_bytes(); original = image[0x16fb6-0x8000:0x17002-0x8000]
    need(len(image) == 76800 and digest(original) == CODE_SHA, 'Exact supplied firmware and original leaf slice')
    contract = source_contract(original)
    ir = (folder/'native.ll').read_text(encoding='utf-8')
    ir_facts = ir_gate(ir,mode)
    objects = []
    for name, log, linked in [('native.o','object.log',False),('COMPONENT-ONLY-NOT-FIRMWARE.elf','linked.log',True)]:
        fact, observed = inspect_elf(folder/name,folder/log,root,original,linked)
        need(observed == contract, 'Object/link/original typed contracts identical')
        objects.append(fact)
    return dict(mode=mode,passed=True,source_sha256=SOURCE_SHA,original=contract,IR=ir_facts,ELFs=objects,
                negative_controls=negatives(original,ir,mode),full_76B_machine_code_equal=True,
                nominal_end='0x17002',physical_IRQ_context_proved=False,vector_mode_proved=False,
                fault_or_async_context_proved=False,complete_firmware_proved=False,firmware_ready=False,
                target_execution=False,ISA_emulation=False,MMIO_execution=False,BIN_generated=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--tool-dir',type=Path,required=True)
    parser.add_argument('--build-root',type=Path)
    parser.add_argument('--replay',type=Path)
    parser.add_argument('--require-firmware-ready',action='store_true')
    args = parser.parse_args(); root = args.project_root.resolve()
    need((args.build_root is None) != (args.replay is None), 'Choose one new build or read-only replay')
    tools, header = load(root,args.tool_dir.resolve())
    frozen = inputs(root,tools,header)
    if args.build_root:
        build = args.build_root.resolve()
        need(build.is_relative_to(HERE/'build') and not build.exists(), 'New owned build directory required')
        build.mkdir(parents=True)
        folders = [build/mode for mode in ('c','cpp')]
        for mode, folder in zip(('c','cpp'),folders):
            folder.mkdir()
            for label, recipe in recipes(folder,mode,tools):
                result = subprocess.run([str(x) for x in recipe],capture_output=True,timeout=120,cwd=root)
                (folder/(label+'.log')).write_bytes(result.stdout+result.stderr)
                need(result.returncode == 0, 'Build command failed: '+label)
            need(inputs(root,tools,header) == frozen, 'Input changed during actual compilation')
            produced = dict(schema='TSL9-IRQ-flag-leaf-build-v1',mode=mode,inputs=frozen,
                            commands=commands(folder,mode,root,tools,header),target_execution=False,BIN_generated=False)
            (folder/'build.json').write_text(json.dumps(produced,indent=2)+'\n',encoding='utf-8')
    else:
        need(args.replay.name == 'verification.json' and args.replay.resolve().is_relative_to(HERE/'build'), 'Owned replay receipt')
        folders = [args.replay.resolve().parent]
    for folder in folders:
        findings = inspect(root,folder,tools,header)
        need(inputs(root,tools,header) == frozen, 'All analysis/source/tool inputs unchanged')
        record = dict(schema='TSL9-IRQ-flag-leaf-static-v1',inputs=frozen,findings=findings,artifacts=inventory(folder))
        if args.replay:
            need(json.loads(args.replay.read_bytes()) == record, 'Exact original, source, artifact, recipe and finding replay equality')
        else:
            (folder/'verification.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(mode=findings['mode'],passed=True,bytes=76,instructions=21,ELFs=2,
                              negative_controls=23,firmware_ready=False,target_execution=False,BIN_generated=False)))
        if args.require_firmware_ready:
            need(findings['firmware_ready'], 'IRQ/vector/hardware/complete firmware context remains unproved')


if __name__ == '__main__':
    try:
        main()
    except ValueError as exc:
        print(json.dumps(dict(passed=False,error=str(exc))))
        sys.exit(1)
