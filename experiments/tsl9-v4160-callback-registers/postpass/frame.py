#!/usr/bin/env python3
"""Reorder two existing callback saves; preserve every other ET_REL byte."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import struct

MODEL = 'experiments/tsl9-v4160-callback-registers'
PARSER = '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
NAME = 'tsl9_callback_native_8614'
BEFORE = [(1, 44), (8, 40), (9, 36), (18, 32), (19, 28), (20, 24),
          (21, 20), (22, 16), (23, 12), (24, 8), (25, 4)]
AFTER = [BEFORE[1], BEFORE[0], *BEFORE[2:]]


def need(value, message):
    if not value:
        raise ValueError(message)


def H(data):
    return hashlib.sha256(data).hexdigest()


def prefix(raw, expected):
    need(len(raw) == 624, 'exact current 624-byte compiled function')
    half = int.from_bytes(raw[:2], 'little')
    need(half & 3 == 1 and half >> 13 == 3 and (half >> 7) & 31 == 2,
         'actual C.ADDI16SP frame entry')
    immediate = (((half >> 12) & 1) << 9) | (((half >> 6) & 1) << 4) | (((half >> 5) & 1) << 6) | (((half >> 3) & 3) << 7) | (((half >> 2) & 1) << 5)
    need(immediate - (1024 if immediate & 512 else 0) == -48, 'actual 48-byte frame')
    rows = []
    for index in range(11):
        half = int.from_bytes(raw[2 + index * 2:4 + index * 2], 'little')
        need(half & 3 == 2 and half >> 13 == 6, 'only existing C.SWSP saves')
        register = (half >> 2) & 31
        offset = (((half >> 9) & 15) << 2) | (((half >> 7) & 3) << 6)
        rows.append((register, offset))
    need(rows == expected, 'exact complete eleven-register save projection')
    return rows


def inspect(root, path):
    parser = next(p for p in (root / 'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py',
                              root / 'apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/elf32.py') if p.is_file())
    need(H(parser.read_bytes()) == PARSER, 'immutable bounded ELF parser')
    E = runpy.run_path(str(parser))['ELF']
    e = E(path)
    need(e.kind == 1 and e.flags == 1 and not e.relocations
         and not any(s['type'] in (4, 9) and s['size'] for s in e.sections),
         'relocatable RVC object with zero REL/RELA relocations')
    functions = [s for s in e.symbols if s['info'] & 15 == 2 and s['size']]
    need(len(functions) == 1, 'one real function only')
    function = functions[0]
    need(function['name'] == NAME and function['info'] == 18 and function['other'] == 0
         and function['size'] == 624 and function['value'] == 0
         and 0 < function['index'] < len(e.sections), 'honest GLOBAL FUNC624 at section start')
    section = e.sections[function['index']]
    need(section['name'] == '.text.' + NAME and section['type'] == 1 and section['flags'] == 6
         and section['address'] == 0 and section['size'] == 624 and section['alignment'] == 2,
         'exact allocated callback section')
    need([s['index'] for s in e.sections if s['flags'] & 2 and s['size']] == [section['index']],
         'no additional allocated code or data')
    for symbol in e.symbols:
        if symbol['index'] == section['index']:
            need(symbol['value'] == 0, 'no interior symbols in reordered function')
    raw = e.raw
    need(len(raw) >= 52 and struct.unpack_from('<H', raw, 40)[0] == 52
         and struct.unpack_from('<H', raw, 44)[0] == 0, 'exact ELF32 header and no program headers')
    table = struct.unpack_from('<I', raw, 32)[0]
    entry_bytes, count = struct.unpack_from('<HH', raw, 46)
    need(entry_bytes == 40 and count == len(e.sections) and table >= 52
         and table + count * 40 <= len(raw), 'whole independent section table')
    intervals = [(0, 52, 'ELF header'), (table, table + count * 40, 'section table')]
    for item in e.sections:
        if item['type'] != 8 and item['size']:
            start, end = item['offset'], item['offset'] + item['size']
            need(0 <= start < end <= len(raw), 'whole declared section storage')
            intervals.append((start, end, item['name']))
    intervals.sort()
    need(all(left[1] <= right[0] for left, right in zip(intervals, intervals[1:])),
         'no aliased file storage or header/section overlap')
    prefix(e.data(section), BEFORE)
    start = section['offset']
    changed = bytearray(raw)
    # Move actual compiled words only. No original BIN byte, opcode encoding,
    # replacement instruction, padding, symbol edit or relocation edit is used.
    changed[start + 2:start + 6] = raw[start + 4:start + 6] + raw[start + 2:start + 4]
    prefix(changed[start:start + 624], AFTER)
    need(changed[:start + 2] == raw[:start + 2] and changed[start + 6:] == raw[start + 6:],
         'every other ELF byte is unchanged')
    return bytes(changed), {'section': section['name'], 'function': function,
                            'file_range': [start + 2, start + 6],
                            'before_save_order': [list(x) for x in BEFORE],
                            'after_save_order': [list(x) for x in AFTER]}


def replay(root, receipt):
    report = json.loads(receipt.read_bytes())
    source, output = Path(report['input']), Path(report['output'])
    owner = (root / MODEL / 'build').resolve()
    need(source.resolve().is_relative_to(owner) and output.resolve().is_relative_to(owner), 'owned actual objects')
    transformed, details = inspect(root, source)
    need(H(source.read_bytes()) == report['input_sha256'] and output.read_bytes() == transformed
         and H(transformed) == report['output_sha256'] and details == report['details'],
         'exact actual existing-word transform replay')
    need(report['runner_sha256'] == H(Path(__file__).read_bytes()), 'current exact frame runner')
    return {'passed': True, 'actual_objects_replayed': True, 'relative_save_order_matched': True,
            'whole_entry_prefix_identical': False, 'original_ABI_admitted': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', required=True, type=Path)
    p.add_argument('--input', type=Path)
    p.add_argument('--output', type=Path)
    p.add_argument('--receipt', type=Path)
    p.add_argument('--replay', type=Path)
    a = p.parse_args()
    root = a.project_root.resolve(strict=True)
    if a.replay:
        need(not any((a.input, a.output, a.receipt)), 'readonly replay has no write parameters')
        print(json.dumps(replay(root, a.replay)))
        return
    need(all((a.input, a.output, a.receipt)), 'explicit input, output and receipt')
    owner = (root / MODEL / 'build').resolve()
    paths = [p.resolve() for p in (a.input, a.output, a.receipt)]
    need(len(set(paths)) == 3 and all(p.is_relative_to(owner) for p in paths), 'distinct owned build paths')
    need(not a.output.exists() and not a.receipt.exists(), 'create-only output and receipt')
    output, details = inspect(root, a.input)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.receipt.parent.mkdir(parents=True, exist_ok=True)
    with a.output.open('xb') as stream:
        stream.write(output)
    report = {'schema': 'TSL9-callback-existing-save-word-order-v1', 'passed': True,
              'input': str(a.input.resolve()), 'input_sha256': H(a.input.read_bytes()),
              'output': str(a.output.resolve()), 'output_sha256': H(output), 'details': details,
              'runner_sha256': H(Path(__file__).read_bytes()), 'function_bytes': 624,
              'relative_save_order_matched': True, 'whole_entry_prefix_identical': False,
              'original_ABI_admitted': False, 'padding_created': False, 'target_execution': False}
    with a.receipt.open('xb') as stream:
        stream.write((json.dumps(report, indent=2) + '\n').encode())
    print(json.dumps(replay(root, a.receipt)))


if __name__ == '__main__':
    main()
