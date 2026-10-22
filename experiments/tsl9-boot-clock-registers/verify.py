#!/usr/bin/env python3
"""Compile/static-read the clock C component, never execute target/MMIO code."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import struct
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODEL = 'experiments/tsl9-boot-clock-registers'
SYMBOL = 'tsl9_boot_clock_registers_2c78'
PARSER = 'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py'
CLASSIFIER = 'analysis/function-hardware/fifty-seventh-round/independent-provider-witness/audit_gp_elf.py'
CLASSIFIER_IMPORT = 'analysis/function-hardware/fifty-fifth-round/independent-service-events-contract/elf_service_events.py'
TOOLS = {
    'clang': '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
    'ld.lld': 'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
    'llvm-objdump': 'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa',
}
SOURCE_PINS = {
    "experiments/tsl9-boot-clock-registers/src/clock_registers.c": "9c40e345a2a66b231018a0f93a6bbfc11fb144adc74eb998d71143f4a4512205",
    "experiments/tsl9-boot-clock-registers/component.ld": "7dadbb06b49cd4dc1f174ddb7ecd45dff65eace2ff34160a6491b30397a99134",
    "experiments/tsl9-v4160-clock-contract/src/clock_contract.c": "0d62c88f3d29262c12f6beb8bc9af566b54046eb1066ded33dd2f58c2f494855",
    "experiments/tsl9-v4160-clock-contract/src/clock_contract.h": "8e86e2740ab7345cd4c12064778de27c881aeddafa507b063f278ff54e2c4d08",
    "experiments/tsl9-v4160-clock-contract/source-map.json": "dca1752dd8c2194ee7df6fb85131ced06d39e9e6d19eea59085fd06b6b5041c5",
    "analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py": "00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141",
    "analysis/function-hardware/fifty-seventh-round/independent-provider-witness/audit_gp_elf.py": "5273de663770fcd57c1d2a40d2158d51928900dff97b0ab37051e1766fcc40f6",
    "analysis/function-hardware/fifty-fifth-round/independent-service-events-contract/elf_service_events.py": "57e3575ad7f56598120abf5639dd660812337693159673adbe6666c8a75b2469",
    "analysis/boot2580-clock-2026-10-22/check.py": "70e2f7a0419e3ee69cd244a7362650efd0777d013ea5ec7d50873570add393fa",
    "analysis/boot2580-clock-2026-10-22/ledger.json": "47e7ac42e902fd632a4ebe2dcf26d6a3c7805c6efc112056ec4dad95be24e8f2",
    "analysis/boot2580-clock-2026-10-22/original_fields.py": "207a9f317a07570988dbddeffca4e39e1f370a7e686d865b0f754364248d5f35",
    "analysis/boot2580-clock-2026-10-22/original-runtime-rows.json": "8072bb26a0166e6c7f9ea59a7d42b594efb4f27376e6d4e31911f2347a0bc43e",
    "analysis/boot2580-clock-exit-2026-10-22/check.py": "403c9f93c37738c10801f33f08e2c5b2232c49cc776cfc32300cb8948a8c54e6",
    "analysis/boot2580-clock-exit-2026-10-22/ledger.json": "2c41f76f470a9c3506adf803015718c50dfb9c74dbac7cfa4d94a9094c22c4a0"
}
BOOT_SHA = '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'
RUNTIME_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BODY_SHA = 'e0debe8b77025cfb56144045a0aa7524b7a2cd2ad0bd3daa2d880408ad9758f5'
CODE_SHA = 'c315b15bf8f1197e6b9e79393538bd33d79c42e6b4833fade55372b4220a881b'
STDINT_SHA = '7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
# Hash of the reviewed complete function IR after removing only source/debug
# metadata attachments, call attribute IDs, whitespace and predecessor comments.
# This preserves every SSA operand, arithmetic operation and branch edge.
IR_BODY_SHA = 'f8c7368d1c73813fc7613ac88b1bd260ccc40b0d45c2406993fc89ce3e42cab9'


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def flags(mode):
    return ['--target=riscv32-unknown-elf', '-march=rv32imac_zicsr_zifencei', '-mabi=ilp32',
            '-Oz', '-mllvm', '-enable-machine-outliner=never', '-ffreestanding', '-fno-builtin',
            '-fno-stack-protector', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
            '-mno-relax', '-ffunction-sections', '-fdata-sections', '-Wall', '-Wextra', '-Werror',
            *['-ffixed-x' + str(n) for n in range(1, 32) if n not in {2, 12, 13, 14, 15}],
            '-x', 'c' if mode == 'c' else 'c++', '-std=c11' if mode == 'c' else '-std=c++17',
            *(['-fno-exceptions'] if mode == 'cpp' else [])]


def recipes(tools, folder, mode):
    source = HERE / 'src/clock_registers.c'
    return [
        ('resource', [tools['clang'], '-print-resource-dir']),
        ('compile', [tools['clang'], *flags(mode), '-c', '-MD', '-MF', folder / 'native.d',
                     '-MT', 'native.o', source, '-o', folder / 'native.o']),
        ('IR', [tools['clang'], *flags(mode), '-S', '-emit-llvm', source, '-o', folder / 'native.ll']),
        ('link', [tools['ld.lld'], '--no-relax', '-T', HERE / 'component.ld', folder / 'native.o',
                  '-o', folder / 'COMPONENT-ONLY-NOT-FIRMWARE.elf']),
        ('disassemble-object', [tools['llvm-objdump'], '--mattr=+m,+a,+c,+zicsr,+zifencei',
                                '-d', '-r', folder / 'native.o']),
        ('disassemble-linked', [tools['llvm-objdump'], '--mattr=+m,+a,+c,+zicsr,+zifencei',
                                '-d', '-r', folder / 'COMPONENT-ONLY-NOT-FIRMWARE.elf']),
    ]


def pins(root, boot, runtime, tools):
    stdint = tools['clang'].parent.parent / 'lib/clang/18/include/stdint.h'
    paths = [Path(__file__).resolve(), *[root / p for p in SOURCE_PINS], boot, runtime, stdint, *tools.values()]
    return {str(p): sha(p) for p in paths}


def dependency_closure(folder, stdint):
    text = (folder / 'native.d').read_text(encoding='utf-8').replace('\\\n', ' ')
    target, sep, tail = text.partition(':')
    paths = {Path(re.sub(r'\\(.)', r'\1', token)).resolve()
             for token in re.findall(r'(?:\\.|[^\s])+', tail)}
    need(sep and target == 'native.o' and paths == {HERE / 'src/clock_registers.c', stdint},
         'Exact native compiler source/stdint closure; model backend is not compiled')
    return {str(p): sha(p) for p in sorted(paths)}


def originals(root, boot, runtime):
    need(sha(boot) == BOOT_SHA and sha(runtime) == RUNTIME_SHA, 'Exact full original BOOT and Runtime')
    b, r = boot.read_bytes(), runtime.read_bytes()
    need(len(b) == 12288 and len(r) == 76800, 'Exact original image sizes')
    # BOOT file base is declared 0x1000, not zero. VA is not a raw file offset.
    boot_body, runtime_body = b[0x1c78:0x1d62], r[0x1074a:0x10834]
    need(len(boot_body) == len(runtime_body) == 234 and boot_body == runtime_body
         and digest(boot_body) == BODY_SHA, 'Whole mapped original 234-byte bodies are identical')
    source_map = json.loads((root / 'experiments/tsl9-v4160-clock-contract/source-map.json').read_bytes())
    need(source_map['firmware_sha256'] == RUNTIME_SHA and source_map['source_base'] == 0x8000
         and source_map['source_bytes'] == 76800 and source_map['instruction_count'] == 93
         and source_map['frame_bytes'] == 16 and source_map['live_stack_offsets'] == [8, 12]
         and source_map['first_poll_mask'] == 0x20000 and source_map['ordinary_unaliased_counter_terminal'] == 4096
         and source_map['PLL_poll_bit'] == 25 and source_map['switch_poll_mask'] == 12
         and source_map['switch_poll_expected'] == 8, 'Pinned source-map contracts')
    ranges = source_map['source_ranges']
    need(len(ranges) == 1 and ranges[0]['address'] == 0x1874a and ranges[0]['bytes'] == 234
         and ranges[0]['sha256'] == BODY_SHA, 'Pinned Runtime raw body mapping')
    exit_ledger = json.loads((root / 'analysis/boot2580-clock-exit-2026-10-22/ledger.json').read_bytes())
    exit_reader = runpy.run_path(str(root / 'analysis/boot2580-clock-exit-2026-10-22/check.py'))
    need(exit_reader['inspect'](root) == exit_ledger, 'Source-backed original exit and caller suffix equality')
    return dict(normal_exit_source_contract=exit_ledger['contract'],
                original_exit_source_check_passed=True,
                original_exit_checker_sha256=sha(root / 'analysis/boot2580-clock-exit-2026-10-22/check.py'),
                caller_suffixes=exit_ledger['callers'], BOOT=dict(VA='[0x2c78,0x2d62)', declared_base='0x1000', file_offset='0x1c78'),
                Runtime=dict(VA='[0x1874a,0x18834)', declared_base='0x8000', file_offset='0x1074a'),
                body_bytes=234, instruction_count_from_source_map=93, body_sha256=BODY_SHA,
                whole_bodies_byte_identical=True)


def normalized_ir(ir):
    match = re.search(r'define[^\n]*@' + SYMBOL + r'\([^)]*\)[^{]*\{(.*?)\n\}', ir, re.S)
    need(match is not None, 'Actual public void function body')
    lines = []
    for raw in match[1].splitlines():
        line = raw.split(';', 1)[0].strip()
        if not line:
            continue
        line = re.sub(r', ![A-Za-z.]+ !\d+', '', line)
        line = re.sub(r' #\d+\b', '', line)
        lines.append(re.sub(r'\s+', ' ', line))
    return '\n'.join(lines) + '\n'


def register_projection_ir(body, blocks, ready_pointer):
    """Check actual two-path SSA values feeding the fixed four-input empty port."""
    post = '\n'.join(blocks['26'])
    samples = re.findall(r'(%\d+) = load volatile i32, ptr ' + re.escape(ready_pointer) + r', align 4', post)
    need(len(samples) == 1, 'One fresh selected-ready stack sample, no extra exit sample')
    selected = samples[0]
    compare = re.search(r'(%\d+) = icmp eq i32 ' + re.escape(selected) + r', 1', post)
    need(compare and ('br i1 ' + compare[1] + ', label %32, label %56') in post,
         'The fresh selected-ready word itself chooses configured versus skipped exit')
    exit_lines = blocks['56']
    phis = [line for line in exit_lines if ' = phi i32 ' in line]
    need(len(phis) == 2, 'Exactly two genuine exit SSA phis')
    a5 = [re.fullmatch(r'(%\d+) = phi i32 \[ 1, %26 \], \[ 8, %52 \]', line) for line in phis]
    a4 = [re.fullmatch(r'(%\d+) = phi i32 \[ ' + re.escape(selected) + r', %26 \], \[ 8, %52 \]', line) for line in phis]
    a5 = [m for m in a5 if m]
    a4 = [m for m in a4 if m]
    need(len(a5) == len(a4) == 1 and a5[0][1] != a4[0][1], 'Fresh W/1 skip inputs and 8/8 configured inputs have correct predecessors')
    port = 'call void asm sideeffect "", "{x12},{x13},{x14},{x15},~{memory}"(i32 131072, i32 1073876992, i32 ' + a4[0][1] + ', i32 ' + a5[0][1] + ')'
    need([line for line in exit_lines if 'asm ' in line] == [port], 'Actual empty fixed A2/A3/A4/A5 input commitment and SSA order')
    return dict(A2='0x20000',A3='0x40021000',
                skipped={'condition':'W=fresh_u32[SP+12] != 1','A4':'W','A5':1},
                configured={'condition':'selected W == 1 and both later polls return normally','A4':8,'A5':8},
                fresh_ready_SSA=selected,A4_phi=a4[0][1],A5_phi=a5[0][1],
                added_MMIO_or_stack_sample=False,conditional_normal_exit_only=True)


def ir_gate(path):
    ir = path.read_text(encoding='utf-8')
    body = normalized_ir(ir)
    need(digest(body.encode()) == IR_BODY_SHA, 'Complete reviewed SSA arithmetic/access/CFG body')
    need('%struct.clock_frame = type { [2 x i32], i32, i32 }' in ir, 'C frame fields at offsets 8 and 12')
    frame = re.search(r'(%\d+) = alloca %struct.clock_frame, align 4', body)
    count = re.search(r'(%\d+) = getelementptr inbounds %struct.clock_frame, ptr (%\d+), i32 0, i32 1', body)
    ready = re.search(r'(%\d+) = getelementptr inbounds %struct.clock_frame, ptr (%\d+), i32 0, i32 2', body)
    need(frame and count and ready and count[2] == ready[2] == frame[1], 'One real 16-byte C frame and shared field pointers')
    empty = 'call void asm sideeffect "", "=*m,~{memory}"(ptr nonnull elementtype(%struct.clock_frame) ' + frame[1] + ')'
    asm_lines = [line for line in body.splitlines() if 'asm ' in line]
    need(len(asm_lines) == 2 and asm_lines[0] == empty, 'Only opaque ASM ports are empty frame-storage and final four-register inputs')
    calls = [line for line in body.splitlines() if re.search(r'\bcall\b', line)]
    need(len(calls) == 4 and sum('@llvm.lifetime.start.p0(i64 16,' in line for line in calls) == 1
         and sum('@llvm.lifetime.end.p0(i64 16,' in line for line in calls) == 1,
         'No external call or helper algorithm; only erased lifetime intrinsics and two empty ports')
    roles = {count[1]: 'count', ready[1]: 'ready'}
    blocks, current = {'entry': []}, 'entry'
    for line in body.splitlines():
        if re.fullmatch(r'\d+:', line):
            current = line[:-1]
            blocks[current] = []
        else:
            blocks[current].append(line)
    need(list(blocks) == ['entry', '16', '23', '26', '32', '43', '47', '52', '56'], 'Exact reviewed three-poll CFG blocks')

    def target(line):
        global_address = re.search(r'ptr inttoptr \(i32 (\d+) to ptr\)', line)
        if global_address:
            address = int(global_address[1])
            need(address in {0x40021000, 0x40021004, 0x40021008}, 'Only declared direct MMIO addresses')
            return address
        field = re.search(r', ptr (%\d+), align 4', line)
        need(field and field[1] in roles, 'Only live count/ready stack fields accessed')
        return roles[field[1]]

    events = {}
    for label, lines in blocks.items():
        events[label] = []
        for line in lines:
            if 'load ' in line:
                need('load volatile i32, ' in line, 'Every data read remains volatile u32')
                events[label].append(['R', target(line)])
            if line.startswith('store '):
                need(line.startswith('store volatile i32 '), 'Every data write remains volatile u32')
                events[label].append(['W', target(line)])
    r0, r4, r8 = 0x40021000, 0x40021004, 0x40021008
    expected = {
        'entry': [['R',r0],['W',r0],['R',r4],['W',r4],['R',r0],['W',r0],['R',r0],['W',r0],
                  ['R',r4],['W',r4],['W',r8],['W','count'],['W','ready'],['R',r0],['W',r0]],
        '16': [['R',r0],['W','ready'],['R','count'],['W','count'],['R','ready']],
        '23': [['R','count']],
        '26': [['R',r0],['W','ready'],['R','ready']],
        '32': [['R',r4],['W',r4],['R',r4],['W',r4],['R',r4],['W',r4],
               ['R',r4],['W',r4],['R',r4],['W',r4],['R',r0],['W',r0]],
        '43': [['R',r0]], '47': [['R',r4],['W',r4],['R',r4],['W',r4]],
        '52': [['R',r4]], '56': [],
    }
    need(events == expected, 'Every volatile MMIO/stack effect remains in its exact CFG block and source order')
    need(sum(kind == 'R' for e in events.values() for kind, _ in e) == 22
         and sum(kind == 'W' for e in events.values() for kind, _ in e) == 20, 'Complete 22-load/20-store static IR instruction inventory')
    branches = []
    gotos = []
    for label, lines in blocks.items():
        for line in lines:
            branch = re.fullmatch(r'br i1 %\d+, label %(\d+), label %(\d+)', line)
            jump = re.fullmatch(r'br label %(\d+)', line)
            if branch:
                branches.append((label, branch[1], branch[2]))
            if jump:
                gotos.append((label, jump[1]))
    need(branches == [('16','23','26'),('23','26','16'),('26','32','56'),('43','43','47'),('52','56','52')]
         and gotos == [('entry','16'),('32','43'),('47','52')], 'Reviewed candidate bounded-first/unbounded-last-two poll edges')
    for start in (0, 2):
        load, store = blocks['32'][start:start + 2]
        value = re.match(r'(%\d+) = load volatile i32, ', load)
        need(value and store.startswith('store volatile i32 ' + value[1] + ', ')
             and target(load) == target(store) == r4, 'Each same-value write retains its own fresh read')
    need('icmp eq i32 %24, 4096' in body and 'icmp eq i32 %21, 0' in body
         and 'icmp eq i32 %30, 1' in body and 'icmp eq i32 %45, 0' in body
         and 'icmp eq i32 %54, 8' in body, 'Fresh counter/ready and both status comparisons retained')
    return dict(normalized_complete_body_sha256=IR_BODY_SHA, volatile_instruction_events=events,
                volatile_load_instructions=22, volatile_store_instructions=20,
                frame_fields={'count': 8, 'ready': 12}, loop_headers=['16','43','52'],
                normal_exit_register_projection=register_projection_ir(body, blocks, ready[1]),
                first_loop_fresh_count_and_ready=True, fresh_postloop_MMIO_read=True,
                two_fresh_same_value_writes=True, final_two_loops_software_timeout_added=False,
                arithmetic_and_SSA_edges_guarded_by_complete_body_hash=True,
                independent_ISA_semantics_proof=False)


def exit_register_gate(rows):
    """Finite critical-field readback only, without executing or modeling the CPU."""
    by = {r['offset']:r for r in rows}
    expected = {
        0x76:('3247','lw',14),0x78:('8547','li',15),0x7a:('631df704','bne',None),
        0xc8:('a147','li',15),0xca:('2147','li',14),0xcc:('5442','lw',13),
        0xce:('b18a','andi',13),0xd0:('e39ef6fe','bne',None),
        0xd4:('37060200','lui',12),0xd8:('b7160240','lui',13),
        0xdc:('4101','addi',2),0xde:('8280','ret',None),
    }
    for offset, values in expected.items():
        need(offset in by and (by[offset]['raw'],by[offset]['mnemonic'],by[offset]['rd']) == values,
             'Actual critical exit opcode/GPR fields: '+hex(offset))
    need(by[0x76]['operands'] == 'a4, 0xc(sp)' and by[0x78]['operands'] == 'a5, 0x1'
         and by[0xc8]['operands'] == 'a5, 0x8' and by[0xca]['operands'] == 'a4, 0x8'
         and by[0xcc]['operands'] == 'a3, 0x4(a2)' and by[0xce]['operands'] == 'a3, a3, 0xc',
         'LLVM confirms fresh W capture and configured 8/8 status polling fields')
    def branch(offset,rs1,rs2,target):
        word = int.from_bytes(bytes.fromhex(by[offset]['raw']),'little')
        need(word & 0x7f == 0x63 and (word>>12)&7 == 1, 'Actual BNE encoding')
        immediate = ((word>>31)<<12)|(((word>>7)&1)<<11)|(((word>>25)&63)<<5)|(((word>>8)&15)<<1)
        if immediate & 4096:
            immediate -= 8192
        need((word>>15)&31 == rs1 and (word>>20)&31 == rs2 and offset+immediate == target,
             'Actual condition register fields and branch destination')
    branch(0x7a,14,15,0xd4)
    branch(0xd0,13,15,0xcc)
    for offset,rd,value in [(0xd4,12,0x20000),(0xd8,13,0x40021000)]:
        word = int.from_bytes(bytes.fromhex(by[offset]['raw']),'little')
        need(word&127 == 0x37 and (word>>7)&31 == rd and word&0xfffff000 == value,
             'Actual common-exit A2/A3 LUI commitments')
    need([r['offset'] for r in rows if r['offset'] >= 0xd4] == [0xd4,0xd8,0xdc,0xde]
         and not [r for r in rows if r['offset'] >= 0xcc and r['rd'] in (14,15)],
         'No later A4/A5 writes after configured values; common exit changes only A2/A3/SP')
    return dict(A2='0x20000',A3='0x40021000',
                skipped={'condition':'fresh W at +0x76 != 1; +0x7a branches to common exit','A4':'W','A5':1},
                configured={'condition':'+0xd0 status BNE eventually falls through','A4':8,'A5':8},
                raw_critical_regions_checked=True,not_full_CPU_semantics_proof=True)


def llvm_rows(root, elf, log, function):
    classifier = runpy.run_path(str(root / CLASSIFIER))
    code = elf.function_bytes(function)
    owner = elf.sections[function['index']]['name']
    rows, current = [], None
    for line in log.read_text(encoding='utf-8').splitlines():
        head = re.match(r'Disassembly of section (.+):', line)
        if head:
            current = head[1]
            continue
        match = re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([^\s]+)\s*(.*)', line)
        if not match:
            continue
        at, raw = int(match[1], 16), bytes.fromhex(match[2])
        offset = at - function['value']
        need(current == owner and offset == sum(len(bytes.fromhex(r['raw'])) for r in rows)
             and len(raw) in (2,4) and raw == code[offset:offset + len(raw)]
             and match[3] not in ('<unknown>','.word','.2byte'), 'Whole executable function LLVM byte readback')
        rd, kind, known = classifier['decode16' if len(raw) == 2 else 'decode32'](int.from_bytes(raw, 'little'))
        need(known and rd in (None,0,2,12,13,14,15), 'Only SP/A2-A5 own writes; no A0/A1/RA/GP/TP/S/T scratch')
        need(match[3] not in ('call','tail','jal','jalr') and (match[3] != 'ret' or offset == 222), 'No call or indirect tail transfer')
        rows.append(dict(offset=offset,raw=raw.hex(),rd=rd,kind=kind,mnemonic=match[3],operands=match[4]))
    need(len(rows) == 91 and sum(len(bytes.fromhex(r['raw'])) for r in rows) == 224, 'Actual 224-byte/91-instruction function')
    sp = [r for r in rows if r['rd'] == 2]
    need([(r['offset'],r['raw']) for r in sp] == [(0,'4111'),(220,'4101')]
         and rows[-1]['raw'] == '8280', 'One balanced 16-byte frame and normal RET')
    stack = [r for r in rows if '(sp)' in r['operands']]
    expected = [(0x42,'sw',8),(0x44,'sw',12),(0x58,'sw',12),(0x5a,'lw',8),(0x5e,'sw',8),
                (0x60,'lw',12),(0x64,'lw',8),(0x74,'sw',12),(0x76,'lw',12)]
    got = []
    for row in stack:
        match = re.fullmatch(r'(?:a[2-5]|zero), (0x[0-9a-f]+)\(sp\)', row['operands'])
        need(match is not None and row['mnemonic'] in ('lw','sw'), 'Only declared u32 stack field accesses')
        got.append((row['offset'],row['mnemonic'],int(match[1],16)))
    need(got == expected, 'Actual live stack +8/+12 read/write sites')
    exit_register_gate(rows)
    return rows


def inspect(root, folder, record):
    need(record['schema'] == 'TSL9-boot-clock-registers-static-component-v1' and record['mode'] in ('c','cpp'), 'Known component receipt')
    for path, pin in SOURCE_PINS.items():
        need(sha(root / path) == pin, 'Pinned tracked source/reference/decoder: ' + path)
    tools = {name:Path(path) for name,path in record['tools'].items()}
    need(set(tools) == set(TOOLS) and all(sha(tools[n]) == pin for n,pin in TOOLS.items()), 'Exact declared existing LLVM binaries')
    boot, runtime = Path(record['boot_firmware']), Path(record['runtime_firmware'])
    original = originals(root, boot, runtime)
    stdint = tools['clang'].parent.parent / 'lib/clang/18/include/stdint.h'
    need(sha(stdint) == STDINT_SHA and record['inputs'] == pins(root,boot,runtime,tools), 'Full unchanged input/resource closure')
    need(Path((folder/'resource.log').read_text().strip())/'include/stdint.h' == stdint, 'Actual compiler resource path')
    need(record['compiler_dependencies'] == dependency_closure(folder, stdint), 'Compiler-observed complete header dependency hashes')
    commands = recipes(tools, folder, record['mode'])
    need(len(commands) == len(record['commands']), 'Complete one-profile command history')
    for actual,(label,argv) in zip(record['commands'],commands):
        need(actual == dict(label=label,argv=[str(x) for x in argv],exit=0,log_sha256=sha(folder/(label+'.log'))),
             'Exact successful compile/link/readback recipe and log')
    Reader = runpy.run_path(str(root/PARSER))['ELF']
    facts = []
    for label,filename,kind in [('object','native.o',1),('linked','COMPONENT-ONLY-NOT-FIRMWARE.elf',2)]:
        elf = Reader(folder/filename)
        definitions = [s for s in elf.symbols if s['info']&15 == 2 and s['size'] and s['index'] not in (0,0xfff1)]
        need(len(definitions) == 1 and definitions[0]['name'] == SYMBOL and definitions[0]['info']>>4 == 1,
             'Exactly one genuine global C function')
        function = definitions[0]
        need(elf.kind == kind and elf.flags == 1, 'Actual RV32/RVC object or component ELF')
        undefined = [s['name'] for s in elf.symbols if s['name'] and s['index'] == 0 and s['info']>>4 in (1,2)]
        absolute = [s['name'] for s in elf.symbols if s['index'] == 0xfff1 and s['info']>>4 in (1,2)]
        need(not undefined and not absolute and not elf.relocations, 'No static UND/ABS provider or relocations')
        allocated = [s for s in elf.sections if s['flags']&2 and s['size']]
        section = '.text.'+SYMBOL if label == 'object' else '.text'
        need([(s['name'],s['size'],s['flags'],s['type']) for s in allocated] == [(section,224,6,1)],
             'Only genuine 224-byte AX allocation; no unwind/writable/NOBITS/carrier section')
        code = elf.function_bytes(function)
        need(len(code) == 224 and digest(code) == CODE_SHA, 'Actual measured candidate body; not an original-byte equality claim')
        if label == 'linked':
            need(function['value'] == struct.unpack_from('<I',elf.raw,24)[0] == 0, 'Explicit nonphysical component VMA zero entry')
        rows = llvm_rows(root,elf,folder/('disassemble-'+label+'.log'),function)
        facts.append(dict(kind=label,function_value=function['value'],function_bytes=224,instructions=91,
                          code_sha256=CODE_SHA,global_functions=[SYMBOL],
                          allocated_sections=[{k:s[k] for k in ('name','size','flags','type','address')} for s in allocated],
                          UND=undefined,global_ABS=absolute,RELA=elf.relocations,LLVM_rows=rows,
                          own_written_GPRs=sorted({r['rd'] for r in rows if r['rd'] not in (None,0)}),
                          normal_exit_register_projection=exit_register_gate(rows)))
    ir = ir_gate(folder/'native.ll')
    return dict(passed=True,actual_artifacts_read=True,mode=record['mode'],original_bodies=original,ELF_facts=facts,IR_facts=ir,
                allowed_own_write_bank=[2,12,13,14,15],no_A0_A1_own_write=True,no_calls=True,stack_frame_bytes=16,
                conditional_normal_exit_projection_only=True,normal_four_GPR_projection_checked=True,
                normal_projection_evidence="Candidate exact SSA phis/fixed-input port and critical raw/LLVM fields; original normal-exit source checker replayed against pinned ledger; not full CPU semantics",
                ordering_gap='Original first MMIO read precedes SP decrement; candidate SP decrement precedes first MMIO read',
                complete_return_register_ABI_proved=False,full_original_ABI_proved=False,whole_original_code_equal=False,
                fault_IRQ_equivalence=False,asynchronous_equivalence=False,installed_ROM_proved=False,
                physical_placement_proved=False,physical_clock_frequency_proved=False,whole_startup_equivalence=False,
                independent_ISA_semantics_proof=False,target_execution=False,HOST_tests_run=False,MMIO_execution=False,
                network=False,BIN_generated=False,rebuilt_flashable_BIN=False)


def replay(root, receipt):
    folder = receipt.parent
    need(folder.is_relative_to(HERE/'build'), 'Owned read-only receipt')
    record = json.loads(receipt.read_bytes())
    inventory = {p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and p != receipt}
    need(record['artifacts'] == inventory, 'Complete actual artifact inventory')
    actual = inspect(root,folder,record)
    need(actual == record['result'], 'Exact read-only object/IR/component replay')
    return actual


def run(argv, folder, label):
    try:
        result = subprocess.run([str(x) for x in argv],cwd=folder,capture_output=True,timeout=120,
                                env=dict(os.environ,TMP=str(folder/'compiler-temp'),TEMP=str(folder/'compiler-temp')))
    except subprocess.TimeoutExpired as error:
        (folder/(label+'.log')).write_bytes((error.stdout or b'')+(error.stderr or b''))
        (folder/'terminal-failure.json').write_bytes((json.dumps(dict(label=label,timed_out=True,retry_performed=False),indent=2)+'\n').encode())
        raise
    log = folder/(label+'.log')
    log.write_bytes(result.stdout+result.stderr)
    if result.returncode:
        (folder/'terminal-failure.json').write_bytes((json.dumps(dict(label=label,exit=result.returncode,retry_performed=False),indent=2)+'\n').encode())
    need(result.returncode == 0, label+' failed; preserve artifacts and stop')
    return dict(label=label,argv=[str(x) for x in argv],exit=result.returncode,log_sha256=sha(log))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',required=True,type=Path)
    p.add_argument('--tool-dir',type=Path)
    p.add_argument('--boot-firmware',type=Path)
    p.add_argument('--runtime-firmware',type=Path)
    p.add_argument('--build-root',type=Path)
    p.add_argument('--replay',type=Path)
    a = p.parse_args()
    root = a.project_root.resolve()
    need(HERE == root/MODEL, 'Canonical model root')
    if a.replay:
        need(not a.tool_dir and not a.boot_firmware and not a.runtime_firmware and not a.build_root, 'Read-only replay arguments')
        print(json.dumps(replay(root,a.replay.resolve())))
        return
    need(a.tool_dir and a.boot_firmware and a.runtime_firmware and a.build_root, 'Explicit local tools/both originals/new output')
    for path,pin in SOURCE_PINS.items():
        need(sha(root/path) == pin, 'Pinned source before compile: '+path)
    boot,runtime = a.boot_firmware.resolve(),a.runtime_firmware.resolve()
    originals(root,boot,runtime)
    tools = {name:(a.tool_dir/(name+('.exe' if os.name == 'nt' else ''))).resolve() for name in TOOLS}
    need(all(sha(tools[n]) == pin for n,pin in TOOLS.items()), 'Pinned existing LLVM before compile')
    need(sha(tools['clang'].parent.parent/'lib/clang/18/include/stdint.h') == STDINT_SHA, 'Pinned actual stdint before compile')
    output = a.build_root.resolve()
    need(output.is_relative_to(HERE/'build') and not output.exists(), 'New owned create-only build')
    frozen = pins(root,boot,runtime,tools)
    output.mkdir(parents=True)
    results = []
    for mode in ('c','cpp'):
        folder = output/mode
        folder.mkdir()
        (folder/'compiler-temp').mkdir()
        commands = [run(argv,folder,label) for label,argv in recipes(tools,folder,mode)]
        record = dict(schema='TSL9-boot-clock-registers-static-component-v1',mode=mode,boot_firmware=str(boot),runtime_firmware=str(runtime),
                      tools={n:str(path) for n,path in tools.items()},inputs=frozen,commands=commands)
        stdint = tools['clang'].parent.parent/'lib/clang/18/include/stdint.h'
        record['compiler_dependencies'] = dependency_closure(folder,stdint)
        record['result'] = inspect(root,folder,record)
        need(frozen == pins(root,boot,runtime,tools), 'Before/after input stability')
        record['artifacts'] = {f.relative_to(folder).as_posix():sha(f) for f in folder.rglob('*') if f.is_file()}
        receipt = folder/'verification.json'
        receipt.write_bytes((json.dumps(record,indent=2)+'\n').encode())
        actual = replay(root,receipt)
        results.append(dict(mode=mode,receipt=str(receipt),receipt_sha256=sha(receipt),candidate_code_sha256=CODE_SHA,
                            passed=actual['passed'],full_original_ABI_proved=False,whole_original_code_equal=False))
    print(json.dumps(dict(passed=True,build_root=str(output),results=results,target_execution=False)))


if __name__ == '__main__':
    main()
