#!/usr/bin/env python3
"""Reorder existing compiler words in two explicit standalone reply ABI regions.

Static ELF editing only. No original firmware is an input; no opcode encoder,
CPU state, instruction execution, or emulation is implemented here.
"""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import struct
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PARSER_SHA = '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
DECODER_SHA = '8ca0cf81d803ebd5aff343542c17cb9cb7a06cd003871e42655aa7e21fb14fd1'
ENTRY = 0x9b8e
FIELDS = ('op', 'rd', 'rs1', 'rs2', 'immediate', 'target', 'memory_width')


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def read_json(path):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            need(key not in out, 'Unique JSON keys: ' + key)
            out[key] = value
        return out
    return json.loads(path.read_text(encoding='utf8'), object_pairs_hook=unique)


def dependency(root, relative_paths, expected):
    matches = [root / path for path in relative_paths if (root / path).is_file()]
    need(len(matches) == 1, 'One exact known dependency location')
    path = matches[0].resolve()
    need(path.is_relative_to(root), 'Dependency remains inside project')
    need(digest(path.read_bytes()) == expected, 'Pinned dependency: ' + path.name)
    return runpy.run_path(str(path))


def context(root):
    root = root.resolve()
    parser = dependency(root, [
        'apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/elf32.py',
        'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py'], PARSER_SHA)
    decoder = dependency(root, [
        'apk-analysis/tsl9-v4160-ota-page-reply-2026-10-22/source-review/source-proof.py',
        'analysis/v4160-ota-page-reply-2026-10-22/source-review/source-proof.py'], DECODER_SHA)
    policy_path = HERE / 'order-policy.json'
    return parser['ELF'], decoder, read_json(policy_path)


def shape(row):
    return tuple(row[field] for field in FIELDS)


def checked_rows(decoder, body):
    rows = decoder['rows'](body)
    need(len(body) == 124 and len(rows) == 50, 'Exact 124B / 50 decoded instructions')
    need(sum(row['bytes'] for row in rows) == 124, 'Complete instruction coverage')
    # The actual unresolved JAL must be the zero-immediate compiler placeholder.
    tx = next(row for row in rows if row['PC'] == ENTRY + 0x52)
    need(tx['op'] == 'jal' and tx['rd'] == 1 and tx['immediate'] is None
         and tx['target'] == ENTRY + 0x52,
         'Actual compiler TX JAL placeholder; target supplied only by RELA')
    normal = [dict(row) for row in rows]
    tx = next(row for row in normal if row['PC'] == ENTRY + 0x52)
    tx['target'] = 0x8a56
    return rows, normal


def owner_contract(elf, policy):
    raw = elf.raw
    need(len(raw) >= 52 and elf.kind == 1 and elf.flags == 1,
         'Standalone ET_REL RV32 RVC soft-float object')
    need(struct.unpack_from('<I', raw, 20)[0] == 1, 'ELF version1')
    need(struct.unpack_from('<I', raw, 24)[0] == 0, 'No ET_REL entrypoint')
    need(struct.unpack_from('<I', raw, 28)[0] == 0
         and struct.unpack_from('<H', raw, 44)[0] == 0, 'No program headers')
    need(struct.unpack_from('<H', raw, 40)[0] == 52, 'Exact ELF32 header')
    need(len(elf.byname) == len(elf.sections), 'Unique ELF section names')
    candidates = [s for s in elf.symbols if s['name'] == policy['symbol']]
    need(len(candidates) == 1, 'Unique exact compiler function')
    symbol = candidates[0]
    need((symbol['value'], symbol['size'], symbol['info'], symbol['other']) == (0, 124, 18, 0),
         'Compiler GLOBAL FUNC124 at section-relative zero')
    need(0 < symbol['index'] < len(elf.sections), 'Defined compiler function')
    section = elf.sections[symbol['index']]
    need((section['name'], section['type'], section['flags'], section['address'],
          section['size'], section['alignment']) == (policy['section'], 1, 6, 0, 124, 2),
         'Exact standalone source section extent / attributes')
    need([s['index'] for s in elf.sections if s['flags'] & 2 and s['size']] == [section['index']],
         'Only one nonempty allocated owner; full-image objects are unsupported')
    need(not any(s['size'] and any(x in s['name'] for x in
             ('eh_frame', 'debug_frame', 'sframe', 'build-id')) for s in elf.sections),
         'No implicit unwind or image-identity metadata')
    need([s['name'] for s in elf.symbols if s['index'] == 0 and s['name']] ==
         ['__tsl9v4160_call_8a56'], 'Sole explicit TX undefined provider')
    need(len(elf.relocations) == 1, 'One actual TX relocation')
    relocation = elf.relocations[0]
    need((relocation['owner'], relocation['offset'], relocation['type'], relocation['addend'],
          relocation['symbol']['name'], relocation['symbol']['index']) ==
         (section['name'], 0x52, 17, 0, '__tsl9v4160_call_8a56', 0),
         'Exact stable R_RISCV_JAL site / undefined target / addend')
    return section


def plan(elf, decoder, policy):
    need(policy['schema'] == 'TSL9-page-reply-source-ABI-order-v1'
         and policy['bytes'] == 124 and policy['instruction_count'] == 50,
         'Explicit page reply ABI policy')
    need([w['interval'] for w in policy['windows']] == [[2, 22], [88, 96]],
         'Only two fixed straight-line ABI intervals')
    section = owner_contract(elf, policy)
    body = elf.data(section)
    rows, normal = checked_rows(decoder, body)
    expected = [tuple(row) for row in decoder['EXPECTED']]
    expected_by_pc = {row[0]: row[1:] for row in expected}
    patches, proofs = [], []
    shoff = struct.unpack_from('<I', elf.raw, 32)[0]
    shend = shoff + len(elf.sections) * 40
    inside = set()
    for rule in policy['windows']:
        lo, hi = rule['interval']
        old = [tuple(x) for x in rule['compiler_order']]
        required = [tuple(x) for x in rule['required_order']]
        need(len(set(old)) == len(old) and set(old) == set(required)
             and len(required) == len(old) and old != required, 'Unique-word semantic permutation')
        selected = [row for row in rows if lo <= row['PC'] - ENTRY < hi]
        need(selected and selected[0]['PC'] == ENTRY + lo
             and selected[-1]['PC'] + selected[-1]['bytes'] == ENTRY + hi,
             'Instruction-aligned exact interval')
        need([shape(row) for row in selected] == old, 'Observed compiler word order, no reapplication')
        need(all(row['op'] in ('sw', 'lw', 'lui') for row in selected),
             'Only declared non-PC-relative memory/register words')
        wanted = [row[1:] for row in expected if lo <= row[0] - ENTRY < hi]
        need(required == wanted, 'Requested order is independently decoded source ABI contract')
        inside.update(row['PC'] for row in selected)
        for symbol in elf.symbols:
            need(not (symbol['index'] == section['index'] and lo <= symbol['value'] < hi),
                 'No symbol or mapping anchor in moved interval')
            if symbol['index'] == section['index'] and symbol['info'] & 15 == 2:
                need(symbol['name'] == policy['symbol'] and symbol['value'] == 0
                     and symbol['size'] == 124, 'No overlapping function owner')
        for relocation in elf.relocations:
            need(not (relocation['owner'] == section['name'] and lo <= relocation['offset'] < hi),
                 'No relocation site in moved interval')
            target = relocation['symbol']
            need(not (target['index'] == section['index'] and
                      lo <= target['value'] + relocation['addend'] < hi),
                 'No relocation target in moved interval')
        start, end = section['offset'] + lo, section['offset'] + hi
        need(start >= 52 and not (start < shend and shoff < end), 'No ELF header/table overlap')
        for other in elf.sections:
            if other['index'] != section['index'] and other['type'] != 8 and other['size']:
                need(not (start < other['offset'] + other['size'] and other['offset'] < end),
                     'No aliased section storage')
        words = {shape(row): body[row['PC'] - ENTRY:row['PC'] - ENTRY + row['bytes']]
                 for row in selected}
        replacement = b''.join(words[key] for key in required)
        need(len(replacement) == hi - lo, 'No padding or new instruction word')
        patches.append((start, end, replacement))
        proofs.append(dict(section_interval=[lo, hi], compiler_order=[list(x) for x in old],
                           required_order=[list(x) for x in required],
                           compiler_words=[words[key].hex() for key in old],
                           required_words=[words[key].hex() for key in required],
                           all_words_from_this_compiler_interval=True))
    for row in normal:
        if row['PC'] not in inside:
            need(shape(row) == expected_by_pc[row['PC']], 'Every unchanged source operand/control anchor')
    result = bytearray(elf.raw)
    for start, end, payload in patches:
        result[start:end] = payload
    need(len(result) == len(elf.raw), 'Exact object extent')
    changed = [i for i, (a, b) in enumerate(zip(elf.raw, result)) if a != b]
    need(changed and all(any(lo <= i < hi for lo, hi, _ in patches) for i in changed),
         'Only declared ABI-window byte changes')
    post_body = bytes(result[section['offset']:section['offset'] + 124])
    _, normal_after = checked_rows(decoder, post_body)
    need([(row['PC'],) + shape(row) for row in normal_after] == expected,
         'All 50 actual scheduled instruction fields equal independent source contract')
    return bytes(result), dict(section=section['name'], symbol=policy['symbol'],
                              words=50, bytes=124, intervals=proofs,
                              changed_file_offsets=changed,
                              before_body_sha256=digest(body), after_body_sha256=digest(post_body))


def paths(root, source, destination, receipt, create):
    values = tuple(path.resolve() for path in (source, destination, receipt))
    need(len(set(values)) == 3, 'Three distinct normalized artifact paths')
    need(all(path.is_relative_to(root) for path in values), 'Artifacts remain in explicit project root')
    need(values[0].is_file(), 'Existing exact compiler input')
    if create:
        need(not values[1].exists() and not values[2].exists(), 'Create-only output and receipt')
    return values


def record(root, source, destination, before, payload, proof):
    return dict(schema='TSL9-page-reply-explicit-ABI-order-receipt-v1', passed=True,
                tool_sha256=digest(Path(__file__).read_bytes()),
                policy_sha256=digest((HERE / 'order-policy.json').read_bytes()),
                parser_sha256=PARSER_SHA, decoder_sha256=DECODER_SHA,
                input=dict(path=source.relative_to(root).as_posix(), bytes=len(before.raw), sha256=digest(before.raw)),
                output=dict(path=destination.relative_to(root).as_posix(), bytes=len(payload), sha256=digest(payload)),
                proof=proof, metadata_symbols_RELA_identical=True,
                compiler_alone_emitted_scheduled_order=False,
                arbitrary_fault_or_async_prefix_equivalence=False,
                original_BIN_read_for_generation=False, new_opcodes_generated=False,
                padding_added=False, compiler_source_provenance_verified_here=False,
                computed_interior_entries_proved_absent=False, unknown_ROM_ABI_proved=False,
                pipeline='C/C++ compiler output followed by explicit source-owned ABI ordering',
                target_execution=False, ISA_emulation=False, hardware=False, OTA_ready=False)


def transform(root, source, destination, receipt):
    root = root.resolve()
    source, destination, receipt = paths(root, source, destination, receipt, True)
    ELF, decoder, policy = context(root)
    before = ELF(source)
    payload, proof = plan(before, decoder, policy)
    value = record(root, source, destination, before, payload, proof)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('xb') as out:
        out.write(payload)
    after = ELF(destination)
    need(before.sections == after.sections and before.symbols == after.symbols
         and before.relocations == after.relocations, 'Actual output metadata/symbols/RELA identical')
    receipt.parent.mkdir(parents=True, exist_ok=True)
    with receipt.open('xb') as out:
        out.write((json.dumps(value, indent=2) + '\n').encode('utf8'))
    return value


def replay(root, receipt):
    root = root.resolve()
    receipt = receipt.resolve()
    need(receipt.is_relative_to(root), 'Receipt inside explicit root')
    value = read_json(receipt)
    source = root / value['input']['path']
    destination = root / value['output']['path']
    source, destination, receipt = paths(root, source, destination, receipt, False)
    ELF, decoder, policy = context(root)
    before, after = ELF(source), ELF(destination)
    payload, proof = plan(before, decoder, policy)
    need(payload == after.raw, 'Actual output equals fresh pure transform result')
    need(before.sections == after.sections and before.symbols == after.symbols
         and before.relocations == after.relocations, 'Actual retained metadata/symbols/RELA')
    need(value == record(root, source, destination, before, payload, proof), 'Exact receipt readback')
    return value


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', type=Path, default=HERE.parents[1])
    p.add_argument('--input', type=Path)
    p.add_argument('--output', type=Path)
    p.add_argument('--receipt', type=Path, required=True)
    p.add_argument('--replay', action='store_true')
    a = p.parse_args()
    if a.replay:
        need(a.input is None and a.output is None, 'Replay takes only a receipt')
        result = replay(a.project_root, a.receipt)
    else:
        need(a.input is not None and a.output is not None, 'Explicit compiler input / output')
        result = transform(a.project_root, a.input, a.output, a.receipt)
    print(json.dumps(dict(passed=True, replay=a.replay, instructions=result['proof']['words'],
                         changed_bytes=len(result['proof']['changed_file_offsets']),
                         compiler_alone_emitted_scheduled_order=False, OTA_ready=False)))
