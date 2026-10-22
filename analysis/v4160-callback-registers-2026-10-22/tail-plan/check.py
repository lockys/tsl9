#!/usr/bin/env python3
"""Inspect original last-eight-byte obligations; never generate replacement data."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy

FW = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
RAW = '6d3c387695703e286429bcdb84a14833868ba6a9f37e03e78d3e1bd391388b7f'
BASE_RAW = 'da17e505ec2b58cada40a80a12a645b7fa21c116ce76666544168f2c4ff6c6a7'


def need(value, message):
    if not value:
        raise ValueError(message)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', required=True, type=Path)
    p.add_argument('--firmware', required=True, type=Path)
    p.add_argument('--receipt', type=Path)
    a = p.parse_args()
    root = a.project_root.resolve()
    parser = next(p for p in (root / 'analysis/v4160-event-callback-2026-10-22/source-review/raw.py',
                              root / 'apk-analysis/tsl9-v4160-event-callback-2026-10-22/source-review/raw.py') if p.is_file())
    need(hashlib.sha256(parser.read_bytes()).hexdigest() == RAW, 'frozen callback operand decoder')
    decode = runpy.run_path(str(parser))['decode']
    base_parser = next(p for p in (root / 'analysis/v4160-ota-tx-2026-10-22/source-review/raw.py',
                                   root / 'apk-analysis/tsl9-v4160-ota-tx-2026-10-22/source-review/raw.py') if p.is_file())
    need(hashlib.sha256(base_parser.read_bytes()).hexdigest() == BASE_RAW, 'frozen base operand decoder')
    base_decode = runpy.run_path(str(base_parser))['decode']
    raw = a.firmware.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == FW, 'actual authenticated original firmware')
    rows = [decode(raw[pc - 0x8000:], pc, base_decode) for pc in (0x8884, 0x8886, 0x888A)]
    expected = [('jalr', 2, 1, 15, 0, None), ('xori', 4, 10, 8, 8, None),
                ('jal', 2, 0, None, None, 0x866C)]
    for row, want in zip(rows, expected):
        got = tuple(row.get(k) for k in ('op', 'bytes', 'rd', 'rs1', 'immediate', 'target'))
        need(got == want, 'original tail call/return operands')
    result = {'schema': 'TSL9-callback-original-tail-obligations-v1', 'passed': True,
              'original_firmware_sha256': FW, 'original_region': [0x8614, 0x888C],
              'new_component_bytes': 624, 'candidate_end_if_placed_at_original_start': 0x8884,
              'remaining_original_range': [0x8884, 0x888C], 'original_tail_bytes': 8,
              'actual_original_tail': rows, 'tail_contains_original_executable_instructions': True,
              'padding_or_tail_replacement_policy_proved': False,
              'entire_original_slot_owned_by_new_C': False, 'placement_admitted': False,
              'target_execution': False, 'ISA_emulation': False, 'BIN_generated': False}
    if a.receipt:
        need(not a.receipt.exists() and a.receipt.resolve() != a.firmware.resolve(), 'create-only distinct receipt')
        a.receipt.parent.mkdir(parents=True, exist_ok=True)
        with a.receipt.open('xb') as stream:
            stream.write((json.dumps(result, indent=2) + '\n').encode())
    print(json.dumps({'passed': True, 'original_tail_instructions': 3, 'original_tail_bytes': 8,
                      'padding_policy_proved': False, 'placement_admitted': False}))


if __name__ == '__main__':
    main()
