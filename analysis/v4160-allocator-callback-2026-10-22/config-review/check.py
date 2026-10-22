#!/usr/bin/env python3
"""Static App configuration fields; do not infer effects of unknown calls."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
FW = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
OLD = 'v4160-ota-source-wiring-2026-10-22/allocator-review'
OLD_CHECK = 'bae75ad424079a6d2c2efe8cd725728b33678d2bef534183088103117bec2aa3'


def need(v, message):
    if not v:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reader(root):
    p = next(p for p in (root / 'analysis' / OLD / 'check.py', root / 'apk-analysis' / ('tsl9-' + OLD) / 'check.py') if p.is_file())
    need(sha(p) == OLD_CHECK, 'Unchanged bounded source-field decoder')
    return runpy.run_path(str(p))['decoder'](root)


def stores(blob, start, decode):
    result = []
    offset = 0
    while offset < len(blob):
        half = int.from_bytes(blob[offset:offset + 2], 'little')
        size = 4 if half & 3 == 3 else 2
        need(offset + size <= len(blob), 'Whole source instruction partition')
        word = int.from_bytes(blob[offset:offset + size], 'little')
        if (size == 4 and word & 0x7f == 0x23) or (size == 2 and half >> 13 == 6 and half & 3 in (0, 2)):
            result.append(decode(blob[offset:], start + offset))
        offset += size
    return result


def gate(rows, writes):
    index = {r['PC']: r for r in rows}

    def field(pc, **items):
        need(all(index[pc][k] == v for k, v in items.items()), 'App config field ' + hex(pc))

    field(0x199e8, op='addi', rd=2, rs1=2, immediate=-96)
    field(0x199f0, op='lui', rd=8, immediate=0x40000)
    field(0x19a20, op='addi', rd=12, rs1=0, immediate=64)
    field(0x19a2e, op='addi', rd=11, rs1=0, immediate=0)
    field(0x19a34, op='lw', rd=15, rs1=8, immediate=0x48)
    field(0x19a36, op='addi', rd=10, rs1=2, immediate=16)
    field(0x19a38, op='jalr', rd=1, rs1=15, immediate=0)
    field(0x19a3a, op='auipc', rd=15, immediate=0x1ffea000)
    field(0x19a3e, op='addi', rd=15, rs1=15, immediate=1874)
    field(0x19a42, op='sw', rs1=2, rs2=15, immediate=16, memory_width=32)
    field(0x19a44, op='lui', rd=15, immediate=0x7000)
    field(0x19a46, op='sh', rs1=2, rs2=15, immediate=20, memory_width=16)
    field(0x19a4a, op='lui', rd=15, immediate=0x08078000)
    field(0x19a4e, op='addi', rd=15, rs1=15, immediate=-1024)
    field(0x19a52, op='sw', rs1=2, rs2=15, immediate=24, memory_width=32)
    field(0x19a7e, op='sw', rs1=2, rs2=14, immediate=72)
    field(0x19a88, op='sw', rs1=2, rs2=14, immediate=76)
    field(0x19ae2, op='lui', rd=15, immediate=0x40000)
    field(0x19ae6, op='lw', rd=15, rs1=15, immediate=0xa4)
    field(0x19aea, op='addi', rd=10, rs1=2, immediate=16)
    field(0x19aec, op='jalr', rd=1, rs1=15, immediate=0)
    need(not any(r['rs1'] == 2 and r['immediate'] < 72 and r['immediate'] + r['memory_width'] // 8 > 68 for r in writes),
         'No explicit SP-relative store overlaps config staCB at SP68..72')
    return dict(MEMAddr=(0x19a3a + index[0x19a3a]['immediate'] + index[0x19a3e]['immediate']) & 0xffffffff,
                MEMLen=index[0x19a44]['immediate'], SNVAddr=index[0x19a4a]['immediate'] + index[0x19a4e]['immediate'],
                config_SP_offset=16, staCB_SP_offset=68)


def inspect(root, firmware=None, layout_receipt=None):
    seal_path = HERE / 'seal.json'
    if seal_path.exists():
        seal = json.loads(seal_path.read_bytes())
        for name, pin in seal['members'].items():
            path = (HERE / name).resolve()
            need(path.is_relative_to(HERE) and sha(path) == pin, 'Closed config evidence member ' + name)
        for name, pin in seal['external_inputs'].items():
            path = root / name
            if name.startswith('analysis/') and not path.is_file():
                path = root / ('apk-analysis/tsl9-' + name.removeprefix('analysis/'))
            need(path.resolve().is_relative_to(root) and sha(path) == pin, 'Immutable config decoder dependency')
    ledger = json.loads((HERE / 'source-ledger.json').read_bytes())
    raw = bytes.fromhex(ledger['body_raw_hex'])
    need(len(raw) == 308 and hashlib.sha256(raw).hexdigest() == ledger['body_sha256'], 'Retained full original body')
    fields = gate(ledger['selected_typed_fields'], ledger['all_standard_store_fields'])
    need(fields['SNVAddr'] == 0x08077c00 and fields['MEMAddr'] == 0x2000418c and fields['MEMLen'] == 0x7000, 'Numeric source configuration')
    result = dict(passed=True, metadata_only=firmware is None and layout_receipt is None,
                  actual_original_firmware_read=False, actual_layout_objects_read=False, numeric_fields=fields,
                  candidate_config_bytes=64, candidate_staCB_offset=52,
                  no_explicit_SP68_store=True, transitive_staCB_zero_or_lifetime_proved=False,
                  installed_ROM_or_Flash_NV_ownership_proved=False, compiler_invoked=False,
                  target_code_executed=False, ISA_emulation=False, hardware_OTA_proved=False)
    if firmware is not None:
        need(sha(firmware) == FW and firmware.stat().st_size == 76800, 'Actual official Runtime identity')
        blob = firmware.read_bytes()[0x119e2:0x11b16]
        need(blob == raw, 'Actual whole308-byte App configuration source')
        decode = reader(root)
        rows = [decode(blob[r['PC'] - 0x199e2:], r['PC']) for r in ledger['selected_typed_fields']]
        writes = stores(blob, 0x199e2, decode)
        need(rows == ledger['selected_typed_fields'] and writes == ledger['all_standard_store_fields'], 'All32 selected fields and23 direct standard stores')
        gate(rows, writes)
        controls = []
        for pc in (0x19a4a, 0x19a52, 0x19aea, 0x19ae6, 0x19ab2):
            original = decode(blob[pc - 0x199e2:], pc)
            found = False
            for bit in range(original['bytes'] * 8):
                changed = bytearray(blob)
                changed[pc - 0x199e2 + bit // 8] ^= 1 << (bit % 8)
                try:
                    mutation = decode(changed[pc - 0x199e2:], pc)
                except ValueError:
                    continue
                unchanged = ('PC', 'op', 'bytes', 'rd', 'rs1', 'rs2', 'memory_width', 'target')
                if any(mutation[k] != original[k] for k in unchanged) or mutation['immediate'] == original['immediate']:
                    continue
                altered = [decode(changed[r['PC'] - 0x199e2:], r['PC']) for r in rows]
                try:
                    gate(altered, stores(changed, 0x199e2, decode))
                except ValueError:
                    controls.append(dict(PC=pc, bit=bit, field='immediate', original=original['immediate'],
                                         mutated=mutation['immediate'], opcode_and_other_fields_unchanged=True, rejected=True))
                    found = True
                    break
            need(found, 'A meaningful raw config operand control ' + hex(pc))
        result.update(actual_original_firmware_read=True, original_bytes=308, selected_fields=32,
                      standard_store_instructions=23, raw_operand_controls=controls)
    if layout_receipt is not None:
        need(firmware is not None, 'Actual layout replay accompanies explicit original firmware')
        module = runpy.run_path(str(HERE / 'probe.py'))
        replay = module['inspect'](root, layout_receipt.parent, json.loads(layout_receipt.read_bytes()))
        need(replay['passed'] and replay['actual_layout_objects_read'], 'Actual two-header layout objects')
        result['actual_layout_objects_read'] = True
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', required=True, type=Path)
    p.add_argument('--firmware', type=Path)
    p.add_argument('--layout-receipt', type=Path)
    a = p.parse_args()
    print(json.dumps(inspect(a.project_root.resolve(), a.firmware, a.layout_receipt)))
