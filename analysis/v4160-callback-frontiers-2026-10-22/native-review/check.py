#!/usr/bin/env python3
"""Independent static ELF/operand/IR review; no target execution or producer replay."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ENTRY = 'tsl9_nv_read_callback_1979a'
MODEL = 'experiments/tsl9-nv-read-callback'
KEYS = ('PC', 'op', 'rd', 'rs1', 'rs2', 'immediate', 'target', 'memory_width')
EXPECTED = [
    (0, 'addi', 2, 2, None, -16, None, None),
    (2, 'sw', None, 2, 1, 12, None, 32),
    (4, 'lui', 13, None, None, 0x40000, None, None),
    (8, 'lw', 15, 13, None, 76, None, 32),
    (10, 'mv', 14, 12, None, None, None, None),
    (12, 'mv', 13, 10, None, None, None, None),
    (14, 'slli', 12, 11, None, 2, None, None),
    (18, 'mv', 10, 14, None, None, None, None),
    (20, 'mv', 11, 13, None, None, None, None),
    (22, 'jalr', 1, 15, None, 0, None, None),
    (24, 'addi', 10, 0, None, 0, None, None),
    (26, 'lw', 1, 2, None, 12, None, 32),
    (28, 'addi', 2, 2, None, 16, None, None),
    (30, 'jalr', 0, 1, None, 0, None, None),
]
TOOLS = {'clang': '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
         'llvm-objdump': 'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}


def need(v, message):
    if not v:
        raise ValueError(message)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_bytes())


def locate(root, name):
    p = root / name
    if name.startswith('analysis/') and not p.is_file():
        p = root / ('apk-analysis/tsl9-' + name.removeprefix('analysis/'))
    return p


def module(p):
    s = importlib.util.spec_from_file_location('nv_native_' + p.parent.name + p.stem, p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def metadata(root):
    s = read(HERE / 'seal.json')
    for name, pin in s['members'].items():
        p = (HERE / name).resolve()
        need(p.is_relative_to(HERE) and sha(p) == pin, 'Independent member ' + name)
    for name, pin in s['external_inputs'].items():
        need(sha(locate(root, name)) == pin, 'Versioned independent dependency ' + name)
    need((HERE / 'README.md').read_bytes() == (HERE / 'readme.zh-TW.md').read_bytes(), 'Traditional Chinese default')
    return dict(passed=True, metadata_only=True, actual_artifacts_read=False,
                target_execution=False, full_original_ABI_proved=False, rebuilt_flashable_BIN=False)


def machine_gate(rows):
    need([tuple(x[k] for k in KEYS) for x in rows] == EXPECTED, 'Reviewed complete call-boundary operand contract')
    # These operands encode: A4=entry A2, A3=entry A0, A2=entry A1<<2;
    # A0=A4 and A1=A3 at the one fresh-slot call. No CPU state is run.


def ir_gate(ir):
    m = re.search(r'^define[^\n]* i32 @' + ENTRY + r'\(([^\n]*)\)[^\n]*\{\n(.*?)^}', ir, re.M | re.S)
    need(m and m[1] == 'i32 noundef %0, i32 noundef %1, i32 noundef %2', 'Three-u32 conditional call surface')
    lines = [x.strip() for x in m[2].splitlines() if x.strip()]
    patterns = [r'%4 = load volatile i32, ptr inttoptr \(i32 262220 to ptr\), align 4, !tbaa !\d+',
                r'%5 = inttoptr i32 %4 to ptr', r'%6 = shl i32 %1, 2',
                r'%7 = tail call (?:noundef )?i32 %5\(i32 noundef %2, i32 noundef %0, i32 noundef %6\) #\d+',
                r'ret i32 0']
    need(len(lines) == len(patterns) and all(re.fullmatch(p, x) for p, x in zip(patterns, lines)),
         'Complete actual IR fresh-slot/word-shift/argument-order/return-zero def-use contract')
    return dict(fresh_slot=0x4004c, call_arguments=['entryA2', 'entryA0', 'uint32(entryA1<<2)'],
                normal_return=0, callee_result_ignored=True, volatile_slot_loads=1)


def controls(blob, fields, ctx, ir):
    rows = fields['rows'](blob, 0, ctx)
    out = []
    for pc, field, label in [(8, 'immediate', 'wrong_ROM_slot'), (14, 'immediate', 'wrong_word_shift'),
                              (20, 'rs1', 'wrong_source_argument'), (2, 'immediate', 'wrong_RA_save_slot'),
                              (22, 'rd', 'call_becomes_tail_jump')]:
        before = next(x for x in rows if x['PC'] == pc)
        found = None
        for bit in range(before['bytes'] * 8):
            raw = bytearray(blob)
            raw[pc + bit // 8] ^= 1 << (bit % 8)
            try:
                changed = fields['rows'](bytes(raw), 0, ctx)
            except ValueError:
                continue
            row = next((x for x in changed if x['PC'] == pc), None)
            if row and row[field] != before[field] and all(row[k] == before[k] for k in KEYS if k != field):
                found = bytes(raw), changed, bit, row[field]
                break
        need(found is not None, 'Single valid raw operand control exists')
        raw, changed, bit, value = found
        try:
            machine_gate(changed)
        except ValueError:
            out.append(dict(case=label, PC=pc, field=field, bit=bit, old=before[field], new=value,
                            mutated_sha256=hashlib.sha256(raw).hexdigest(), rejected=True))
        else:
            raise ValueError('Accepted incorrect native operand')
    for label, before, after in [('slot_not_volatile', 'load volatile i32', 'load i32'),
                                 ('byte_count_not_words', 'shl i32 %1, 2', 'shl i32 %1, 0'),
                                 ('source_destination_swapped', 'i32 noundef %2, i32 noundef %0', 'i32 noundef %0, i32 noundef %2')]:
        need(ir.count(before) == 1, 'Unique actual IR control site')
        changed = ir.replace(before, after, 1)
        try:
            ir_gate(changed)
        except ValueError:
            out.append(dict(case=label, mutated_IR_sha256=hashlib.sha256(changed.encode()).hexdigest(), rejected=True))
        else:
            raise ValueError('Accepted incorrect native IR')
    return out


def inspect(root, folder):
    record = read(folder / 'verification.json')
    need(record['mode'] in ('c', 'cpp'), 'Actual language mode')
    for path, pin in record['source_pins'].items():
        need(sha(path) == pin, 'Actual source/tool/header identity')
    tools = {n: Path(p) for n, p in record['tools'].items()}
    need(set(tools) == set(TOOLS) and all(sha(tools[n]) == p for n, p in TOOLS.items()), 'Independent local LLVM identities')
    native = module(locate(root, 'analysis/v4160-resident-native-2026-10-22/implementation/probe.py'))
    flags = native.flags(record['mode'])
    src = root / MODEL / 'src/nv_read_callback.c'
    recipes = [('compiler-resource-dir', [tools['clang'], '-print-resource-dir']),
               ('native-object', [tools['clang'], *flags, '-c', '-MD', '-MF', folder / 'native.d', '-MT', 'native.o', src, '-o', folder / 'native.o']),
               ('native-IR', [tools['clang'], *flags, '-S', '-emit-llvm', src, '-o', folder / 'native.ll']),
               ('complete-static-disassembly', [tools['llvm-objdump'], '--mattr=+m,+a,+c,+zicsr,+zifencei', '-d', '-r', folder / 'native.o'])]
    need([(c['label'], c['argv']) for c in record['commands']] == [(n, [str(x) for x in a]) for n, a in recipes], 'One exact ordinary C/C++ recipe')
    for c in record['commands']:
        need(c['exit'] == 0 and c['log'] == c['label'] + '.log' and sha(folder / c['log']) == c['log_sha256'], 'Actual successful command log')
    need(record['artifacts'] == {p.relative_to(folder).as_posix(): dict(bytes=p.stat().st_size, sha256=sha(p))
                                  for p in folder.rglob('*') if p.is_file() and p.name != 'verification.json'}, 'Entire actual artifact inventory')
    resource = Path((folder / 'compiler-resource-dir.log').read_text().strip()) / 'include/stdint.h'
    need(sha(resource) == '7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34', 'Pinned resource stdint')
    deptext = (folder / 'native.d').read_text().replace('\\\n', ' ')
    lhs, _, rhs = deptext.partition(':')
    deps = {Path(re.sub(r'\\(.)', r'\1', x)).resolve() for x in re.findall(r'(?:\\.|[^\s])+', rhs)}
    need(lhs == 'native.o' and deps == {src, src.with_suffix('.h'), resource}, 'Independent complete -MD closure')
    old = module(locate(root, 'analysis/v4160-adc-config-2026-10-22/model-review/native.py'))
    raw_reader, (_, fields, llvm, ctx) = old.context(root)
    e = ctx['ELF'](folder / 'native.o')
    funcs = [f for f in e.symbols if f['info'] & 15 == 2 and f['size']]
    alloc = [s for s in e.sections if s['flags'] & 2 and s['size']]
    need(e.kind == 1 and e.flags == 1 and len(funcs) == len(alloc) == 1, 'Actual RV32/RVC ET_REL and complete single function')
    f, sec = funcs[0], alloc[0]
    need(f['name'] == ENTRY and f['info'] == 18 and f['other'] == 0 and f['value'] == 0 and f['index'] == sec['index']
         and f['size'] == sec['size'] == 32 and sec['type'] == 1 and sec['flags'] == 6, 'Whole real GLOBAL FUNC32 code allocation')
    need(not e.relocations and not any(s['name'] and s['index'] == 0 for s in e.symbols)
         and not any(s['info'] >> 4 and s['index'] == 0xfff1 for s in e.symbols), 'UND0 RELA0 ABS0')
    blob = e.function_bytes(f)
    rows = fields['rows'](blob, 0, ctx)
    parsed = raw_reader.parse_sections((folder / 'complete-static-disassembly.log').read_text(), llvm)
    need([{k: v for k, v in x.items() if k != 'offset'} for x in rows] == parsed[sec['name']], 'Independent raw fields equal all LLVM static operands')
    machine_gate(rows)
    ir = (folder / 'native.ll').read_text()
    ir_result = ir_gate(ir)
    negative = controls(blob, fields, ctx, ir)
    return dict(passed=True, actual_artifacts_read=True, mode=record['mode'], functions=1, bytes=32, instructions=14,
                UND=0, RELA=0, ABS=0, unused_real_functions=0, code_sha256=hashlib.sha256(blob).hexdigest(),
                fresh_slot=0x4004c, indirect_calls=1, IR=ir_result, controls=negative,
                own_written_GPRs=[1, 2, 10, 11, 12, 13, 14, 15], extra_own_A3_write=True, frame_bytes=16,
                slot_read_after_frame_save=True, original_slot_read_before_frame_save=True,
                normal_call_projection_supported=True, scope='isolated conditional call argument/effect/result boundary',
                required_premises=['fresh slot maps to reviewed copy projection and returns normally',
                                   'valid aligned disjoint private frame and ordinary accesses',
                                   'no asynchronous observation or modification',
                                   'C indirect call surface matches actual callee register contract'],
                full_original_ABI_proved=False, resident_caller_replacement_proved=False,
                fault_or_IRQ_equivalence=False, original_extent_fit=False, installed_ROM_proved=False,
                target_execution=False, producer_replay_called=False, linked=False, new_BIN=False, rebuilt_flashable_BIN=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', required=True, type=Path)
    p.add_argument('--folder', type=Path)
    p.add_argument('--receipt', type=Path)
    p.add_argument('--replay', type=Path)
    a = p.parse_args()
    root = a.project_root.resolve()
    result = metadata(root)
    if a.replay:
        need(a.folder is None and a.receipt is None, 'Read-only replay mode')
        record = read(a.replay)
        need(record['checker_sha256'] == sha(HERE / 'check.py'), 'Independent reader identity')
        result = inspect(root, Path(record['folder']))
        need(result == record['result'], 'Independent actual replay equality')
    elif a.folder:
        need(a.receipt is not None and not a.receipt.exists(), 'Create-only independent receipt')
        result = inspect(root, a.folder.resolve())
        a.receipt.parent.mkdir(parents=True, exist_ok=True)
        a.receipt.write_bytes((json.dumps(dict(checker_sha256=sha(HERE / 'check.py'), folder=str(a.folder.resolve()), result=result), indent=2) + '\n').encode())
    else:
        need(a.receipt is None, 'Receipt only with actual folder')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
