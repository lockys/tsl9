#!/usr/bin/env python3
"""Bounded static BLE-init defaults and the first post-copy opaque callback."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
TD_SHA = 'd18a5c4d0722e20d3d0398f180931118a5125c9ada56a64d32c602ad5bd71490'
CALLBACK_PIN = 'd460886bab54b1a9d4ac288de09b38b2b1874aa806b07e5c049eaa6abe2bc401'
FW_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def locate(root, name):
    path = root / name
    if name.startswith('analysis/') and not path.is_file():
        path = root / ('apk-analysis/tsl9-' + name.removeprefix('analysis/'))
    return path


def previous(root):
    folder = locate(root, 'analysis/v4160-allocator-callback-2026-10-22/callback-review/seal.json').parent
    need(sha(folder / 'seal.json') == CALLBACK_PIN, 'Closed callback-prefix source')
    for name, pin in json.loads((folder / 'seal.json').read_bytes())['members'].items():
        need(sha(folder / name) == (pin if isinstance(pin, str) else pin['sha256']), 'Closed callback member ' + name)
    return runpy.run_path(str(folder / 'check.py'))


def decoder(root):
    fallback = previous(root)['decoder'](root)

    def decode(raw, pc):
        half = int.from_bytes(raw[:2], 'little')
        # Conditional Xwchc QK_C_LBU, from the pinned TableGen source. This is
        # a static operand decoder, not a CPU state transition or emulator.
        if half & 3 == 0 and half >> 13 == 1:
            return dict(PC=pc, bytes=2, raw_hex=raw[:2].hex(), op='qk.c.lbu',
                        rd=8 + ((half >> 2) & 7), rs1=8 + ((half >> 7) & 7), rs2=None,
                        immediate=((half >> 12) & 1) + ((half >> 10) & 3) * 8 + ((half >> 5) & 3) * 2,
                        target=None, memory_width=8)
        return fallback(raw, pc)

    return decode


def gate(record):
    rows = record['rows']
    start = record['entry']
    need(len(rows) == 92 and sum(r['bytes'] for r in rows) == 228, 'Complete228-byte92-row init body')
    index = {r['PC'] - start: r for r in rows}

    def field(offset, **fields):
        need(all(index[offset][k] == v for k, v in fields.items()), 'Init continuation field ' + hex(offset))

    field(0x46, op='lui', rd=8, immediate=0x20003000)
    field(0x6e, op='addi', rd=15, rs1=8, immediate=record['config_base'] - 0x20003000)
    stores = [(0x7a, 'qk.c.sh', 12, 16), (0x82, 'qk.c.sb', 14, 8),
              (0x8a, 'qk.c.sh', 16, 16), (0x92, 'qk.c.sb', 15, 8),
              (0x9a, 'qk.c.sb', 18, 8), (0xa2, 'qk.c.sb', 19, 8),
              (0xaa, 'qk.c.sb', 20, 8), (0xb4, 'qk.c.sb', 22, 8)]
    actual_stores = [r for r in rows if start + 0x6e <= r['PC'] < start + 0xba and r['op'] in ('sb', 'sh', 'sw', 'qk.c.sb', 'qk.c.sh')]
    need(len(actual_stores) == 8, 'All eight default stores in the bounded interval')
    for offset, op, displacement, width in stores:
        field(offset, op=op, rs1=15, rs2=14, immediate=displacement, memory_width=width)
        need(displacement + width // 8 <= 52, 'Default write misses complete staCB word')
    for offset, displacement, op, base in [(0x7c, 14, 'qk.c.lbu', 15), (0x8c, 15, 'qk.c.lbu', 15),
                                            (0x94, 18, 'qk.c.lbu', 15), (0x9c, 19, 'qk.c.lbu', 15),
                                            (0xa0, 15, 'qk.c.lbu', 15), (0xa4, 20, 'qk.c.lbu', 15),
                                            (0xac, 22, 'qk.c.lbu', 9)]:
        field(offset, op=op, rd=14, rs1=base, immediate=displacement, memory_width=8)
    interval = [r for r in rows if start + 0x6e <= r['PC'] < start + 0xb6]
    need(all(r['rd'] in (None, 0, 14) or r['PC'] == start + 0x6e for r in interval), 'No hidden S1 or config-base destination before callback load')
    need(not any(r['op'] in ('jal', 'jalr') and r['rd'] == 1 for r in interval), 'No opaque call between copy return and callback load')
    field(0xb6, op='lw', rd=15, rs1=15, immediate=44, memory_width=32)
    field(0xb8, op='beq', rs1=15, rs2=0, target=start + 0xc4)
    field(0xba, op='jalr', rd=1, rs1=15, immediate=0)
    field(0xce, op='jal', rd=1, target=record['next_init_target'])
    for offset in (0xdc, 0xe2):
        field(offset, op='jalr', rd=0, rs1=1, immediate=0)
    need(all(r['target'] is None or start <= r['target'] < start + 228
             or (r['op'] == 'jal' and r['PC'] == start + 0xce) for r in rows), 'All direct branches and final direct call accounted for')
    return dict(default_store_offsets=[x[2] for x in stores], default_stores_miss_staCB=True,
                first_post_copy_opaque_call=start + 0xba, callback_pointer_field=44,
                callback_word=record['config_base'] + 44, next_direct_init_target=record['next_init_target'],
                callback_or_later_runtime_effects_proved=False)


def controls(raw, record, decode, row_reader):
    out = []
    for offset, field_name in [(0x7c, 'immediate'), (0x82, 'immediate'), (0xb6, 'immediate')]:
        before = next(r for r in record['rows'] if r['PC'] == record['entry'] + offset)
        chosen = None
        for bit in range(before['bytes'] * 8):
            changed = bytearray(raw)
            changed[offset + bit // 8] ^= 1 << (bit % 8)
            try:
                after = decode(changed[offset:], before['PC'])
            except ValueError:
                continue
            stable = ('bytes', 'op', 'rd', 'rs1', 'rs2', 'target', 'memory_width')
            if after[field_name] == before[field_name] or any(after[k] != before[k] for k in stable):
                continue
            mutated = dict(record, rows=row_reader(changed, record['entry'], decode))
            try:
                gate(mutated)
            except ValueError:
                chosen = dict(offset=offset, bit=bit, field=field_name, before=before[field_name], after=after[field_name], rejected=True)
                break
        need(chosen is not None, 'Valid same-shape raw operand control')
        out.append(chosen)
    return out


def actual(root, refs, firmware):
    C = previous(root)
    td = refs / 'instruction-reference/RISCVInstrInfoXwch.td'
    need(sha(td) == TD_SHA, 'Pinned conditional Xwchc format')
    need(sha(firmware) == FW_SHA, 'Original App firmware identity')
    fw = firmware.read_bytes()
    app_rows = C['rows'](fw[0x11a8a:0x11ab4], 0x19a8a, C['decoder'](root))
    index = {r['PC']: r for r in app_rows}
    need(index[0x19a92]['op'] == 'auipc' and index[0x19a92]['rd'] == 15 and index[0x19a92]['immediate'] == 0
         and index[0x19a96]['op'] == 'addi' and index[0x19a96]['rd'] == 15 and index[0x19a96]['rs1'] == 15
         and index[0x19a96]['immediate'] == -674
         and index[0x19a9e]['op'] == 'sw' and index[0x19a9e]['rs1'] == 2
         and index[0x19a9e]['rs2'] == 15 and index[0x19a9e]['immediate'] == 60, 'Actual App callback value stored at config+44')
    decode = decoder(root)
    records = []
    negative = []
    for item in C['candidate_data'](root, refs):
        entry = item['slot400A4']
        raw = item['segment'][entry - 0x40000:entry - 0x40000 + 228]
        record = dict(candidate=item['candidate'], entry=entry, config_base=item['config_destination'],
                      body_sha256=hashlib.sha256(raw).hexdigest(), raw_hex=raw.hex(),
                      next_init_target=0x43bca if item['candidate'] == 'carrier' else 0x43b3e,
                      rows=C['rows'](raw, entry, decode))
        gate(record)
        negative.extend(dict(candidate=item['candidate'], **x) for x in controls(raw, record, decode, C['rows']))
        records.append(record)
    return dict(schema='TSL9-init-defaults-source-v1', candidates=records, App_callback_source_rows=app_rows,
                conditional_App_config_field44_value=0x197f0, raw_controls=negative,
                installed_identity_or_callback_lifetime_proved=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', type=Path, required=True)
    p.add_argument('--candidate-root', type=Path)
    p.add_argument('--firmware', type=Path)
    p.add_argument('--capture', action='store_true')
    a = p.parse_args()
    root = a.project_root.resolve()
    need((a.candidate_root is None) == (a.firmware is None), 'Both actual source inputs or metadata only')
    ledger = HERE / 'ledger.json'
    if a.capture:
        need(a.candidate_root is not None and not ledger.exists(), 'Create-only actual-source capture')
        result = actual(root, a.candidate_root, a.firmware)
        ledger.write_bytes((json.dumps(result, indent=2) + '\n').encode())
    expected = json.loads(ledger.read_bytes())
    facts = [gate(r) for r in expected['candidates']]
    if a.candidate_root is not None:
        need(actual(root, a.candidate_root, a.firmware) == expected, 'Actual source byte/operand/control replay')
    if (HERE / 'seal.json').exists():
        seal = json.loads((HERE / 'seal.json').read_bytes())
        for name, pin in seal['members'].items():
            need(sha(HERE / name) == pin, 'Closed continuation member ' + name)
        for name, pin in seal['external_inputs'].items():
            need(sha(locate(root, name)) == pin, 'Closed continuation dependency ' + name)
    print(json.dumps(dict(passed=True, metadata_only=a.candidate_root is None,
                          actual_candidate_bodies_read=0 if a.candidate_root is None else 2,
                          candidate_body_bytes=228, rows_per_body=92, conditional_QK_C_LBU=True,
                          raw_controls_replayed=a.candidate_root is not None, raw_controls=6 if a.candidate_root is not None else 0,
                          facts=facts, conditional_App_field44_callback=0x197f0,
                          SDK_field_name_inferred='tsCB/temperature; header-order inference, no fresh offsetof44 probe',
                          config_word_zero_beyond_first_opaque_callback_proved=False,
                          installed_identity_proved=False, target_execution=False, ISA_emulation=False,
                          hardware_OTA_proved=False, new_BIN=False)))


if __name__ == '__main__':
    main()
