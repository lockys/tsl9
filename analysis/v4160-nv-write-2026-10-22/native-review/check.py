#!/usr/bin/env python3
"""Independent actual native ELF/raw operands/LLVM/IR review; no target execution."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import source
import ir as semantic_ir
import native_fields

MODEL = 'experiments/tsl9-nv-write-callback'
FLASH = 'experiments/tsl9-v4160-flash-entry-order/src'
KEYS = ('PC', 'op', 'rd', 'rs1', 'rs2', 'immediate', 'target', 'memory_width')
TOOLS = {'clang': '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
         'llvm-objdump': 'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}
RESOURCE = '7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
need, sha, read, locate, module = source.need, source.sha, source.read, source.locate, source.module


def metadata(root):
    seal = read(HERE / 'seal.json')
    for name, pin in seal['members'].items():
        p = (HERE / name).resolve()
        need(p.is_relative_to(HERE) and sha(p) == pin, 'Independent member ' + name)
    for name, pin in seal['external_inputs'].items():
        need(sha(locate(root, name)) == pin, 'Independent external input ' + name)
    original_folder = locate(root, 'analysis/v4160-nv-write-2026-10-22/source-review')
    source.closed(original_folder, '2d9c5278019c0a2e452f42cc2cadf8af60b486c95244cd1b855567b5fc060005')
    need(read(original_folder / 'ledger.json')['groups'] == read(HERE / 'original-contract.json')['groups'], 'Independent original raw source agrees with separately sealed source review')
    implementation_seal = locate(root, 'analysis/v4160-nv-write-2026-10-22/implementation/seal.json')
    need(sha(implementation_seal) == 'e4889ef4828275d2bf3199ba6c61fa9d3ebdbb6c094243d64036b31d287de764', 'Exact producer final source freeze')
    for row in read(implementation_seal)['members']:
        need(sha(locate(root, row['path'])) == row['sha256'], 'Closed producer member ' + row['path'])
    need((HERE / 'README.md').read_bytes() == (HERE / 'readme.zh-TW.md').read_bytes(), 'Traditional Chinese default')
    original = source.inspect(root)
    context(root)
    return dict(passed=True, metadata_only=True, original=original, actual_artifacts_read=False,
                full_original_ABI_proved=False, target_execution=False, new_BIN=False)


def context(root):
    old = module(locate(root, 'analysis/v4160-adc-config-2026-10-22/model-review/native.py'))
    reader, (prior, fields, llvm, ctx) = old.context(root)
    fields, llvm, ctx = native_fields.attach(root, source, fields, llvm, ctx)
    return reader, (prior, fields, llvm, ctx)


def kernel(name, rows):
    expected = read(HERE / 'native-kernels.json')
    need([[x[k] for k in KEYS] for x in rows] == expected[name], 'Complete actual raw operand contract ' + name)


def raw_controls(blobs, fields, ctx):
    config = read(HERE / 'control-sites.json')
    out = []
    for trial in config:
        name, pc, field = trial['function'], trial['PC'], trial['field']
        blob = blobs[name]
        before = next(x for x in fields['rows'](blob, 0, ctx) if x['PC'] == pc)
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
        need(found is not None, 'Valid single-field machine operand negative ' + trial['case'])
        raw, changed, bit, value = found
        try:
            kernel(name, changed)
        except ValueError:
            out.append(dict(case=trial['case'], function=name, PC=pc, field=field, bit=bit,
                            old=before[field], new=value, mutated_sha256=hashlib.sha256(raw).hexdigest(), rejected=True))
        else:
            raise ValueError('Accepted wrong raw operand ' + trial['case'])
    return out


def ir_controls(text):
    trials = read(HERE / 'ir-controls.json')
    out = []
    for trial in trials:
        need(text.count(trial['before']) == 1, 'Unique actual IR negative site ' + trial['case'])
        changed = text.replace(trial['before'], trial['after'], 1)
        try:
            semantic_ir.contract(changed)
        except ValueError:
            out.append(dict(case=trial['case'], mutated_IR_sha256=hashlib.sha256(changed.encode()).hexdigest(), rejected=True))
        else:
            raise ValueError('Accepted wrong static IR ' + trial['case'])
    return out


def inspect(root, folder):
    record = read(folder / 'verification.json')
    need(record['schema'] == 'TSL9-real-NV-write-timer-C-v1' and record['mode'] in ('c', 'cpp'), 'Actual native recipe and language')
    tools = {name: Path(p) for name, p in record['tools'].items()}
    need(set(tools) == set(TOOLS) and all(sha(tools[n]) == h for n, h in TOOLS.items()), 'Independent pinned LLVM identities')
    old = module(locate(root, 'analysis/v4160-resident-native-2026-10-22/implementation/probe.py'))
    flags = old.flags(record['mode'])
    src = root / MODEL / 'src/nv_write_callback.c'
    recipes = [('compiler-resource-dir', [tools['clang'], '-print-resource-dir']),
               ('native-object', [tools['clang'], *flags, '-c', '-MD', '-MF', folder / 'native.d', '-MT', 'native.o', src, '-o', folder / 'native.o']),
               ('native-IR', [tools['clang'], *flags, '-S', '-emit-llvm', src, '-o', folder / 'native.ll']),
               ('complete-static-disassembly', [tools['llvm-objdump'], '--mattr=+m,+a,+c,+zicsr,+zifencei', '-d', '-r', folder / 'native.o'])]
    need([(c['label'], c['argv']) for c in record['commands']] == [(n, [str(x) for x in a]) for n, a in recipes], 'One exact ordinary first-profile recipe, no fixed-bank or adaptive flags')
    for c in record['commands']:
        need(c['exit'] == 0 and c['log'] == c['label'] + '.log' and sha(folder / c['log']) == c['log_sha256']
             and c['TMP'] == c['TEMP'] == str(folder / 'compiler-temp'), 'Actual successful log and owned temporary directory')
    need(record['artifacts'] == {p.relative_to(folder).as_posix(): dict(bytes=p.stat().st_size, sha256=sha(p))
                                  for p in folder.rglob('*') if p.is_file() and p.name != 'verification.json'}, 'Entire actual artifact inventory')
    for path, pin in record['source_pins'].items():
        need(sha(path) == pin, 'Actual source/tool/runner/header identity')
    resource = Path((folder / 'compiler-resource-dir.log').read_text().strip()) / 'include/stdint.h'
    need(sha(resource) == RESOURCE, 'Actual pinned compiler stdint resource')
    deptext = (folder / 'native.d').read_text().replace('\\\n', ' ')
    lhs, _, rhs = deptext.partition(':')
    deps = {Path(re.sub(r'\\(.)', r'\1', x)).resolve() for x in re.findall(r'(?:\\.|[^\s])+', rhs)}
    expected_deps = {src, src.with_suffix('.h'), *[root / FLASH / n for n in ('flash_native.c', 'flash_native.h', 'native_io.h')], resource}
    need(lhs == 'native.o' and deps == expected_deps, 'Independent complete -MD source/header/resource closure')
    need(all(str(p) in record['source_pins'] for p in expected_deps), 'Every actual compiler dependency was pinned')
    binding = 'analysis/v4160-callback-frontiers-2026-10-22/binding-review/'
    implementation = locate(root, 'analysis/v4160-nv-write-2026-10-22/implementation')
    pinned_inputs = expected_deps | {Path(sys.executable).resolve(), *tools.values(),
        locate(root, 'analysis/v4160-resident-native-2026-10-22/implementation/probe.py'), old.parser(root),
        locate(root, 'analysis/function-hardware/fifty-seventh-round/independent-provider-witness/audit_gp_elf.py'),
        locate(root, 'analysis/function-hardware/fifty-fifth-round/independent-service-events-contract/elf_service_events.py'),
        *[locate(root, binding + n) for n in ('seal.json', 'ledger.json', 'check.py')],
        *[implementation / n for n in ('probe.py', 'source-proof.json', 'original-write-197be.bin', 'original-timer-19764.bin')]}
    need(set(record['source_pins']) == {str(p) for p in pinned_inputs}, 'Complete exact source/tool/runner/retained-evidence pin set')
    reader, (_, fields, llvm, ctx) = context(root)
    e = ctx['ELF'](folder / 'native.o')
    funcs = [f for f in e.symbols if f['info'] & 15 == 2 and f['size']]
    alloc = [s for s in e.sections if s['flags'] & 2 and s['size']]
    names = set(semantic_ir.HELPERS + [semantic_ir.WRITE, semantic_ir.TIMER])
    need(e.kind == 1 and e.flags == 1 and len(funcs) == len(alloc) == 8 and {f['name'] for f in funcs} == names,
         'RV32/RVC ET_REL, all eight genuine functions and allocations')
    need(all(f['info'] == 18 and f['other'] == 0 and f['value'] == 0 and f['size'] == e.sections[f['index']]['size'] for f in funcs)
         and {f['index'] for f in funcs} == {s['index'] for s in alloc}
         and all(s['type'] == 1 and s['flags'] == 6 for s in alloc), 'Every allocation exactly one complete global C function')
    need(not any(s['name'] and s['index'] == 0 for s in e.symbols)
         and not any(s['info'] >> 4 and s['index'] == 0xfff1 for s in e.symbols), 'UND0 and global ABS0')
    parsed = reader.parse_sections((folder / 'complete-static-disassembly.log').read_text(), llvm)
    blobs, all_rows, functions = {}, {}, []
    for f in funcs:
        name = f['name']
        blob = e.function_bytes(f)
        blobs[name] = blob
        rows = fields['rows'](blob, 0, ctx)
        all_rows[name] = rows
        need([{k: v for k, v in x.items() if k != 'offset'} for x in rows] == parsed[e.sections[f['index']]['name']], 'All raw operand fields agree with complete LLVM text ' + name)
        kernel(name, rows)
        written = sorted({x['rd'] for x in rows if x['rd'] not in (None, 0)})
        functions.append(dict(name=name, bytes=len(blob), instructions=len(rows), code_sha256=hashlib.sha256(blob).hexdigest(),
                              own_written_GPRs=written,
                              stack_accesses=[{k: x[k] for k in KEYS} for x in rows if x['memory_width'] and x['rs1'] == 2],
                              SP_adjustments=[dict(PC=x['PC'], delta=x['immediate']) for x in rows if x['rd'] == x['rs1'] == 2 and x['op'] == 'addi']))
    need(set(parsed) == {s['name'] for s in alloc}, 'No omitted or hidden disassembled allocation')
    for r in e.relocations:
        need(r['symbol']['name'] in names and r['symbol']['index'] not in (0, 0xfff1) and r['addend'] == 0
             and r['type'] in (17, 19), 'Each actual relocation targets a genuine defined provider entry')
    reloc = [dict(owner=r['owner'], offset=r['offset'], type=r['type'], addend=r['addend'], target=r['symbol']['name']) for r in e.relocations]
    need(reloc == read(HERE / 'relocation-contract.json'), 'Every actual C/ASM provider relocation and order')
    irtext = (folder / 'native.ll').read_text()
    IR = semantic_ir.contract(irtext)
    quarter = semantic_ir.bodies(irtext)['tsl9_flash_quarter_9c0a'][1]
    missing = []
    for match in re.finditer(r'asm sideeffect "jal ra, ([A-Za-z0-9_]+)", "([^"]+)"', quarter):
        name, constraints = match.groups()
        declared = {int(n) for n in re.findall(r'(?:=|~)\{x(\d+)\}', constraints)}
        actual = {x['rd'] for x in all_rows[name] if x['rd'] not in (None, 0)}
        for reg in sorted(actual - declared):
            missing.append(dict(callee=name, register=reg))
    need(missing == [dict(callee='tsl9_flash_unlock_18e98', register=11),
                     dict(callee='tsl9_flash_erase_18ec4', register=11)], 'Actual unused quarter ASM declaration gaps remain explicit')
    qrows = all_rows['tsl9_flash_quarter_9c0a']
    need(not any(11 in (x['rs1'], x['rs2']) for x in qrows if 0x14 <= x['PC'] < 0x26),
         'Exact unused quarter has no intervening encoded A1 read before fresh source reload')
    need({x['rd'] for x in all_rows[semantic_ir.TIMER] if x['rd'] not in (None, 0)} == {11, 12}, 'Native timer preserves normal A0 but changes A1/A2')
    leaf_names = [n for n in semantic_ir.HELPERS if 'quarter' not in n]
    protected = {1, 2, 3, 4, 5, 6, 7, 8, 9, 17, *range(18, 32)}
    need(not any(x['rd'] in protected for n in leaf_names for x in all_rows[n]), 'All actual flash leaves preserve structural/T/A7 bank')
    controls = raw_controls(blobs, fields, ctx) + ir_controls(irtext)
    interpretation = read(HERE / 'machine-findings.json')
    return dict(passed=True, schema='TSL9-nv-write-independent-native-v1', actual_artifacts_read=True,
                language=record['mode'], functions=functions, global_functions=8,
                unused_genuine_functions=['tsl9_flash_status_18e90', 'tsl9_flash_quarter_9c0a'],
                allocated_bytes=sum(s['size'] for s in alloc), instructions=sum(f['instructions'] for f in functions),
                UND=0, RELA=len(reloc), global_ABS=0, relocations=reloc, IR=IR, controls=controls,
                unused_quarter_missing_ASM_clobbers=missing,
                interpretation=interpretation, actual_MD_inputs=[dict(path=str(p), sha256=sha(p)) for p in sorted(deps)],
                normal_effect_projection_only=True, full_original_ABI_proved=False,
                fault_or_IRQ_equivalence=False, installed_provider_proved=False,
                original_extent_fit_proved=False, placement_proved=False, physical_compatibility_proved=False,
                producer_replay_called=False, target_execution=False, HOST_tests_run=False,
                ISA_emulation=False, network=False, hardware=False, linked=False, new_BIN=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', required=True, type=Path)
    p.add_argument('--folder', type=Path)
    p.add_argument('--receipt', type=Path)
    p.add_argument('--replay', type=Path)
    p.add_argument('--firmware', type=Path)
    a = p.parse_args()
    root = a.project_root.resolve()
    result = metadata(root)
    if a.firmware:
        need(a.folder is None and a.replay is None, 'Firmware source-only proof mode')
        result = source.inspect(root, a.firmware.resolve())
    elif a.replay:
        need(a.folder is None and a.receipt is None, 'Read-only replay mode')
        record = read(a.replay)
        need(record['checker_sha256'] == sha(HERE / 'check.py'), 'Independent checker identity')
        if record['kind'] == 'firmware':
            result = source.inspect(root, Path(record['firmware']))
        else:
            need(record['kind'] == 'native', 'Explicit actual receipt kind')
            result = inspect(root, Path(record['folder']))
        need(result == record['result'], 'Actual independent read-only replay equality')
    elif a.folder:
        need(a.receipt is not None and not a.receipt.exists(), 'Create-only actual review receipt')
        result = inspect(root, a.folder.resolve())
    else:
        need(a.receipt is None, 'Receipt only for explicit actual source or object proof')
    if a.receipt:
        need(not a.receipt.exists(), 'Create-only receipt')
        a.receipt.parent.mkdir(parents=True, exist_ok=True)
        a.receipt.write_bytes((json.dumps(dict(checker_sha256=sha(HERE / 'check.py'),
            kind='firmware' if a.firmware else 'native',
            folder=str(a.folder.resolve()) if a.folder else None,
            firmware=str(a.firmware.resolve()) if a.firmware else None, result=result), indent=2) + '\n').encode())
    print(json.dumps(result))


if __name__ == '__main__':
    main()
