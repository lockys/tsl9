#!/usr/bin/env python3
"""Conditional candidate byte-fill footprint, static fields only; no CPU state."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PRIOR = 'v4160-ota-source-wiring-2026-10-22/allocator-review/check.py'
PIN = 'c65cb2622eeade943b85aed00ca23a16552b64e229a0fbd839599f537de6fe6a'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def need(v, message):
    if not v:
        raise ValueError(message)


def prior(root):
    path = next(p for p in (root / 'analysis' / PRIOR, root / 'apk-analysis' / ('tsl9-' + PRIOR)) if p.is_file())
    need(sha(path) == PIN, 'Pinned candidate reader')
    return runpy.run_path(str(path))


def gate(rows):
    need(len(rows) == 14, 'Complete46-byte14-row byte-fill leaf')
    index = {r['PC']: r for r in rows}
    base = 0x2000039c

    def field(offset, **items):
        need(all(index[base + offset][k] == v for k, v in items.items()), 'Candidate fill field ' + hex(base + offset))

    field(0, op='lui', rd=14, immediate=0x40024000)
    field(4, op='lw', rd=15, rs1=14, immediate=0x20c, memory_width=32)
    field(8, op='sw', rs1=14, rs2=0, immediate=0x20c, memory_width=32)
    field(12, op='fence.i')
    field(16, op='beq', rs1=10, rs2=0, target=base + 24)
    field(18, op='add', rd=14, rs1=10, rs2=12)
    field(22, op='bne', rs1=12, rs2=0, target=base + 34)
    field(24, op='lui', rd=14, immediate=0x40024000)
    field(28, op='sw', rs1=14, rs2=15, immediate=0x20c, memory_width=32)
    field(32, op='jalr', rd=0, rs1=1, immediate=0)
    field(34, op='addi', rd=10, rs1=10, immediate=1)
    field(36, op='sb', rs1=10, rs2=11, immediate=-1, memory_width=8)
    field(40, op='bne', rs1=10, rs2=14, target=base + 34)
    field(44, op='jal', rd=0, target=base + 24)
    need(all(r['rd'] in (None, 0, 10, 14, 15) for r in rows), 'No explicit S/GP/SP/RA destination')
    need(not any(r['op'] in ('jal', 'jalr') and r['rd'] == 1 for r in rows), 'No nested call')


def config_derivation(root, firmware=None):
    scope = 'v4160-allocator-callback-2026-10-22/config-review'
    old = next(p for p in (root / 'analysis' / scope, root / 'apk-analysis' / ('tsl9-' + scope)) if p.is_dir())
    ledger = json.loads((old / 'source-ledger.json').read_bytes())
    mac = HERE.parent / 'mac-review'
    need(sha(mac / 'seal.json') == '3e653f961ed1309babad68506af791768e6ea615a201e52b4570fb6f65be8a76', 'Exact helper proof seal')
    for name, pin in json.loads((mac / 'seal.json').read_bytes())['members'].items():
        need(sha(mac / name) == pin, 'Closed MAC footprint member')
    module = runpy.run_path(str(mac / 'check.py'))
    facts = module['gate'](json.loads((mac / 'ledger.json').read_bytes())['groups'])
    need(facts['caller_helper_write_SP_offsets'] == [8, 13]
         and facts['caller_copy_write_SP_offsets'] == [40, 45]
         and not facts['entire_caller_slice_explicitly_writes_staCB'], 'Exact local post-zero helper footprints')
    group = {r['PC']: r for r in ledger['selected_typed_fields']}
    need(group[0x19a20]['immediate'] == 64 and group[0x19a2e]['immediate'] == 0
         and group[0x19a36]['immediate'] == 16 and group[0x19a34]['immediate'] == 0x48
         and group[0x19aea]['immediate'] == 16, 'Original zero request and final same relative config pointer')
    writes = [r for r in ledger['all_standard_store_fields'] if 0x19a38 < r['PC'] < 0x19aec]
    need(all(r['immediate'] + r['memory_width'] // 8 <= 68 or r['immediate'] >= 72 for r in writes if r['rs1'] == 2), 'All local post-zero explicit stack stores miss staCB')
    other = [r for r in writes if r['rs1'] != 2]
    need(len(other) == 1 and (other[0]['PC'], other[0]['op'], other[0]['rs1'], other[0]['immediate']) == (0x19aca, 'sb', 14, 23), 'Only post-zero indirect store is the reviewed six-byte loop')
    source = bytes.fromhex(ledger['body_raw_hex'])
    decode = prior(root)['decoder'](root)
    calls = []
    at = 0
    while at < len(source):
        half = int.from_bytes(source[at:at + 2], 'little')
        size = 4 if half & 3 == 3 else 2
        word = int.from_bytes(source[at:at + size], 'little')
        pc = 0x199e2 + at
        call = (size == 4 and word & 0x7f in (0x6f, 0x67) and (word >> 7) & 31 == 1)
        call |= size == 2 and ((half & 3 == 1 and half >> 13 == 1) or
                              (half & 3 == 2 and half >> 12 == 9 and (half >> 2) & 31 == 0 and (half >> 7) & 31 != 0))
        if call and 0x19a38 < pc < 0x19aec:
            calls.append(decode(source[at:], pc))
        at += size
    need(len(calls) == 1 and calls[0]['PC'] == 0x19ab4 and calls[0]['target'] == 0x18f56, 'Only nested call after zero request and before BLE entry is the reviewed helper')
    actual = False
    if firmware is not None:
        data = firmware.read_bytes()
        need(len(data) == 76800 and hashlib.sha256(data).hexdigest() == ledger['firmware_sha256']
             and data[0x119e2:0x11b16] == source, 'Actual original App config body')
        helper = json.loads((mac / 'ledger.json').read_bytes())['groups']['helper']
        expected = b''.join(bytes.fromhex(r['raw_hex']) for r in helper)
        need(data[0x10f56:0x10f88] == expected, 'Actual helper footprint bytes')
        actual = True
    need(set(range(68, 72)).issubset(range(16, 80)) and not set(range(68, 72)).intersection(range(8, 14))
         and not set(range(68, 72)).intersection(range(40, 46)), 'Pure source-interval containment and disjointness')
    return dict(kind='Static operand/interval derivation, not CPU-state execution', actual_App_and_helper_bytes_read=actual,
                premises=['Setup branch reached; the selected reference slot48 leaf is the called implementation',
                          'App SP+16 is nonnull, its64 bytes are valid and do not alias MMIO or code; normal memory/MMIO completion and no asynchronous stack/register modifications',
                          'The fixed decoded source remains unchanged; no self-modification or hidden transfer'],
                zero_request_byte_range_relative_to_App_SP=[16, 79], staCB_byte_range=[68, 71],
                conditional_staCB_zero_at_BLE_call_entry=True, installed_or_live_staCB_zero_proved=False,
                version_gate_reachability_not_proved=True, BLE_initializer_may_change_source_or_live_S1=True,
                runtime_callback_lifetime_or_A2_independence_proved=False,
                next_boundary='Inside BLE_LibInit before config copy, including prior numeric200004BC call')


def inspect(root, candidate_root=None, firmware=None):
    ledger = json.loads((HERE / 'source-ledger.json').read_bytes())
    if (HERE / 'seal.json').exists():
        seal = json.loads((HERE / 'seal.json').read_bytes())
        for name, pin in seal['members'].items():
            path = (HERE / name).resolve()
            need(path.is_relative_to(HERE) and sha(path) == pin, 'Closed byte-fill member ' + name)
        for name, pin in seal['external_inputs'].items():
            path = root / name
            if name.startswith('analysis/') and not path.is_file():
                path = root / ('apk-analysis/tsl9-' + name.removeprefix('analysis/'))
            need(sha(path) == pin, 'Exact byte-fill source dependency')
    for item in ledger['candidates']:
        body = b''.join(bytes.fromhex(r['raw_hex']) for r in item['rows'])
        need(len(body) == 46 and hashlib.sha256(body).hexdigest() == item['body_sha256'], 'Metadata row byte closure')
        gate(item['rows'])
    result = dict(passed=True, metadata_only=candidate_root is None, actual_candidate_bodies_read=0,
                  candidate_leaf_bytes=46, candidate_leaf_rows=14,
                  normal_byte_fill_footprint='[initial A0, initial A0+A2) modulo32, only when nonnull and length nonzero',
                  zero_or_null_still_performs_MMIO=True, MMIO_address=0x4002420c,
                  no_explicit_S_GP_SP_RA_writes=True, normal_fill_return='advanced A0; not libc original-pointer semantics',
                  physical_effects_or_installed_identity_proved=False, target_execution=False,
                  ISA_emulation=False, hardware_OTA_proved=False)
    need((candidate_root is None) == (firmware is None), 'Use both explicit candidate-root and firmware, or metadata only')
    result['config_entry_derivation'] = config_derivation(root, firmware)
    if candidate_root is None:
        return result
    C = prior(root)
    decode = C['decoder'](root)
    controls = []
    for source, expected in zip(C['inputs'](root, candidate_root), ledger['candidates']):
        path = candidate_root / source['candidate'] / expected['segment']
        data = path.read_bytes()
        slot = int.from_bytes(data[0x48:0x4c], 'little')
        flash = source['mapped_core_flash'] + slot - 0x20000040
        need(sha(path) == expected['segment_sha256'] and slot == expected['RAM_entry'] and flash == expected['mapped_flash'], 'Actual source mapping and slot')
        blob = data[flash - 0x40000:flash - 0x40000 + 46]
        actual = C['rows'](blob, slot, decode)
        need(actual == expected['rows'], 'Actual complete byte-fill fields')
        gate(actual)
        for offset, key in ((4, 'immediate'), (36, 'immediate'), (40, 'target')):
            original = next(r for r in actual if r['PC'] == slot + offset)
            found = False
            for bit in range(original['bytes'] * 8):
                changed = bytearray(blob)
                changed[offset + bit // 8] ^= 1 << (bit % 8)
                try:
                    row = decode(changed[offset:], slot + offset)
                except ValueError:
                    continue
                same = ('PC', 'bytes', 'op', 'rd', 'rs1', 'rs2', 'memory_width')
                if any(row[k] != original[k] for k in same) or row[key] == original[key]:
                    continue
                try:
                    gate(C['rows'](changed, slot, decode))
                except ValueError:
                    controls.append(dict(candidate=source['candidate'], PC=slot + offset, bit=bit, field=key,
                                         original=original[key], mutated=row[key], same_instruction_shape=True, rejected=True))
                    found = True
                    break
            need(found, 'Valid single-operand fill control')
    result.update(metadata_only=False, actual_candidate_bodies_read=2, actual_raw_operand_controls=controls)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', required=True, type=Path)
    p.add_argument('--candidate-root', type=Path)
    p.add_argument('--firmware', type=Path)
    a = p.parse_args()
    print(json.dumps(inspect(a.project_root.resolve(), a.candidate_root, a.firmware)))
