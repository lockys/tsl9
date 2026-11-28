"""Audit a fresh source-only selected build; never run firmware."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import struct
import re

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ELF = runpy.run_path(str(ROOT / 'src/native/tx_candidate/postpass/elf32.py'))['ELF']


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def diagnostic_header(elf):
    need(elf.kind == 2 and struct.unpack_from('<I', elf.raw, 24)[0] == 0, 'diagnostic executable with entry zero')
    phoff = struct.unpack_from('<I', elf.raw, 28)[0]
    size, count = struct.unpack_from('<HH', elf.raw, 42)
    need(not count or size == 32 and phoff >= 52 and phoff + count * size <= len(elf.raw),
         'bounded diagnostic program headers')
    need(not any(struct.unpack_from('<I', elf.raw, phoff + i * size)[0] == 1 for i in range(count)),
         'diagnostic has no PT_LOAD')


def uuid_owner(elf):
    spans = sorted((s for s in elf.sections if s['flags'] & 2 and s['size']
                    and s['address'] < 0x1ab48 and s['address'] + s['size'] > 0x1ab44),
                   key=lambda s: s['address'])
    need([(s['address'], s['size'], s['flags'], s['type']) for s in spans]
         == [(0x1ab44, 2, 2, 1), (0x1ab46, 2, 2, 1)], 'unique UUID/tail section ownership')
    need([elf.data(s) for s in spans] == [bytes.fromhex('f1ff'), bytes(2)], 'UUID and retained tail bytes')
    for name, address, owner in [('tsl9_gatt_write_UUID_1ab44', 0x1ab44, spans[0]),
                                  ('tsl9_opaque_gap_0001ab46', 0x1ab46, spans[1])]:
        symbols = [s for s in elf.symbols if s['name'] == name]
        need(len(symbols) == 1, 'one named DATA owner')
        s = symbols[0]
        need((s['value'], s['size'], s['info'], s['other'], s['index'])
             == (address, 2, 17, 0, owner['index']), 'UUID/tail symbol extent and ownership')
    need(not any(s['name'] == 'tsl9_opaque_gap_0001ab44' for s in elf.symbols), 'obsolete opaque UUID owner removed')


def tx_owner(elf):
    spans = [s for s in elf.sections if s['flags'] & 2 and s['size']
             and s['address'] < 0x8b6e and s['address'] + s['size'] > 0x8a56]
    need(len(spans) == 1 and (spans[0]['address'], spans[0]['size'], spans[0]['type'], spans[0]['flags'])
         == (0x8a56, 280, 1, 6), 'unique exact TX allocation')
    need(sha(elf.data(spans[0])) == '3b01d76ded6b08cb239ca3c8d7e789db8b0b7149d4c6d4e48c50d987a1ef2f0b',
         'TX original instruction bytes')
    for name, value, size in [('__tsl9v4160_call_8a56', 0x8a56, 8),
                              ('tsl9_filter_external_8a56', 0x8a56, 0),
                              ('tsl9_tx_oversized_return', 0x8b6c, 2)]:
        symbols = [s for s in elf.symbols if s['name'] == name]
        need(len(symbols) == 1, 'unique actual TX public binding')
        symbol = symbols[0]
        need((symbol['value'], symbol['size'], symbol['info'], symbol['other'], symbol['index'])
             == (value, size, 18, 0, spans[0]['index']), 'real TX entry and return ownership')


def defaults_owner(elf):
    owners = [s for s in elf.sections if s['flags'] & 2 and s['size']
              and s['address'] < 0x1a6a0 and s['address'] + s['size'] > 0x1a69c]
    need(len(owners) == 1, 'unique defaults allocation')
    owner = owners[0]
    need((owner['address'], owner['size'], owner['type'], owner['flags']) == (0x1a69c, 4, 1, 2)
         and elf.data(owner) == bytes.fromhex('31323334'), 'exact four readonly defaults bytes')
    symbols = [s for s in elf.symbols if s['name'] == 'tsl9_settings_default_data_1a69c']
    need(len(symbols) == 1, 'one genuine defaults symbol')
    s = symbols[0]
    need((s['value'], s['size'], s['info'], s['other'], s['index']) == (0x1a69c, 4, 17, 0, owner['index']),
         'section-backed defaults provider, not ABS or oversized alias')


def audit(folder, original):
    support = runpy.run_path(str(ROOT / 'scripts/source-build-support.py'))
    manifest = support['metadata']()
    provenance = runpy.run_path(str(ROOT / 'scripts/verify-curated-source.py'))['metadata']()
    need(len(provenance['files']) == len(manifest['files']) == 176, 'complete registered source inventory')
    record = json.loads((folder / 'NOT-FLASHABLE-spans.json').read_bytes())
    need(len(record['outputs']) == 2 and record['candidate_bytes_read'] == 0
         and not record['excluded_read'] and not record['complete_firmware']
         and not record['flashable'], 'bounded source-only span receipt')
    mapping = json.loads((ROOT / 'src/compact-layout.json').read_bytes())
    need(sha(original) == '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667', 'original image identity')
    need(len(original) == 76800, 'original length')
    expected_ranges = [(0x8000, 0x14056), (0x14c8a, 0x1ac00)]
    rows = []
    all_memory = []
    for mode, receipt in zip(('c', 'cpp'), record['outputs']):
        need(receipt['mode'] == mode, 'mode receipt order')
        expected_units = {u['name'] for u in manifest['native_units'] + manifest['native_data_units']}
        expected_units.update([manifest['window']['name'], manifest['opaque']['name']])
        objects = list((folder / 'build' / 'source' / mode).glob('*/unit.o'))
        need(len(objects) == 142 and {p.parent.name for p in objects} == expected_units,
             'all registered units have fresh output objects')
        elf = ELF(folder / 'build' / ('NOT-FLASHABLE-compact-source-layout-' + mode + '.elf'))
        diagnostic_header(elf)
        uuid_owner(elf)
        defaults_owner(elf)
        tx_owner(elf)
        original_unit = folder / 'build/source/tx' / ('symbolic-' + mode + '.o')
        tx_library = runpy.run_path(str(ROOT / 'src/native/tx_candidate/verify-original.py'))
        tx_library['check_unit'](tx_library['ELF'](original_unit))
        runpy.run_path(str(ROOT / 'scripts/relative_table_owner.py'))['check_relative_table_owner'](elf)
        spans = sorted((s for s in elf.sections if s['flags'] & 2 and s['size']), key=lambda s: s['address'])
        need(len(spans) == 6269, 'fresh selected section count')
        memory = {}
        for s in spans:
            start, end = s['address'], s['address'] + s['size']
            need(s['type'] == 1 and any(lo <= start < end <= hi for lo, hi in expected_ranges), 'permitted selected range')
            for i, byte in enumerate(elf.data(s)):
                need(start + i not in memory, 'no overlapping allocated bytes')
                memory[start + i] = byte
        need(len(memory) == 73676, 'selected byte count retained')
        payload = bytes(memory[p] for p in sorted(memory))
        need(sha(payload) == mapping['selected_linked_sha256'] == receipt['sha256'], 'unchanged selected linked bytes')
        binary = (folder / ('NOT-FLASHABLE-selected-spans-' + mode + '.bin')).read_bytes()
        need(binary == payload, 'span file equals fresh linked ELF bytes')
        need([(s['start'], s['end']) for s in receipt['spans']] == expected_ranges, 'exact selected spans')
        differences = [p for p, byte in memory.items() if byte != original[p - 0x8000]]
        need(not differences, 'every selected byte equals original')
        need(bytes(memory[p] for p in (0x1ab44, 0x1ab45)) == original[0x12b44:0x12b46], 'UUID agrees with original bytes')
        unresolved = sorted({s['name'] for s in ELF(folder / 'build' / 'source' / ('NOT-FLASHABLE-candidate-aliases-' + mode + '.o')).symbols
                             if s['name'] and s['index'] == 0 and s['info'] >> 4 in (1, 2)})
        need(set(unresolved) == {'__tsl9v4160_data_2000b18c', 'tsl9_boot_resident_40000',
                                'tsl9_incoming_external_14056', 'tsl9_input_state_decoders_static_data_1ab48',
                                'tsl9_record_field_transitions_static_data_1a078',
                                'tsl9_registered_callbacks_static_data_1a638', 'tsl9_runtime_reset_stack_top'},
             'source aggregate keeps exact seven dependencies before stack witness')
        need(not (folder / 'build' / ('STRICT-' + mode + '.elf')).exists(), 'strict link produced no firmware')
        rows.append({'mode': mode, 'selected_sections': len(spans), 'selected_bytes': len(memory),
                     'selected_sha256': sha(payload), 'original_differences': len(differences), 'unresolved_before_stack_witness': unresolved})
        all_memory.append(memory)
    need(all_memory[0] == all_memory[1], 'C11/C++17 identical original-coordinate bytes')
    paths = ['src/source-manifest.json', 'src/source-build-manifest.json', 'src/compact-layout.json',
             'src/native/receive/defaults_read_window.c', 'src/native/receive/gatt_write_uuid.c', 'src/native/receive/opaque_allowed_gaps.c',
             'scripts/source-build-support.py', 'scripts/verify-source-aggregate.py',
             'scripts/build-compact-source-layout.py', 'scripts/build-source-spans.py',
             'scripts/relative_table_owner.py', 'experiments/v4160-gatt-uuid-source-extension/origin.c',
             'experiments/v4160-original-tx-integrated/check.py', 'experiments/v4160-defaults-integrated/spec.json']
    paths += ['src/native/tx_candidate/original_tx.c', 'src/native/tx_candidate/verify-original.py', 'scripts/source-ota-epilogue.py', 'scripts/verify-conditional-tx-storage.py',
              'scripts/verify-conditional-data-providers.py', 'scripts/verify-conditional-full-payload-link.py',
              'scripts/build-v4160-source-candidate.py', 'experiments/v4160-original-tx-integrated/test_tx.py']
    paths += sorted(set(re.findall(r'src/native/receive/[A-Za-z0-9_]+\.inc',
                                  (ROOT / 'scripts/source-ota-epilogue.py').read_text('utf-8'))))
    return {'passed': True, 'source_files': 176, 'CODE_units': 125, 'DATA_units': 15,
            'fresh_registered_objects_per_language': 142, 'modes': rows,
            'original_TX_integrated': True, 'selected_bytes_added': 0,
            'historical_objects_used_for_build': False, 'candidate_used_for_build': False,
            'new_flashable_BIN': False, 'target_executed': False,
            'inputs_sha256': {p: sha((ROOT / p).read_bytes()) for p in paths}}


def audit_full(folder, original):
    receipt = json.loads((folder / 'verification.json').read_bytes())
    conditional = folder / 'conditional-link'
    link_receipt = json.loads((conditional / 'verification.json').read_bytes())
    need(receipt['passed'] and link_receipt['passed'], 'actual candidate and full link receipts')
    need(len(receipt['outputs']) == 2 and len(link_receipt['results']) == 2, 'both language receipts present')
    need(not receipt['hardware_validated'] and not receipt['flashable_proved']
         and not link_receipt['installed_rom_proved'] and not link_receipt['global_index_bounds_proved'],
         'retain diagnostic and conditional limits')
    modes = []
    for mode, row in zip(('c', 'cpp'), link_receipt['results']):
        need(row['mode'] == mode and row['strict_undefined'] == ['tsl9_boot_resident_40000']
             and row['registered_defaults_section_backed'] and row['section_backed_new_symbols'] == 1
             and row['negative_section_controls'] == 2 and row['conditional_data_aliases'] == 3,
             'one source-code addition, real defaults and retained negative controls')
        elf = ELF(conditional / ('NOT-FLASHABLE-conditional-full-' + mode + '.elf'))
        diagnostic_header(elf)
        uuid_owner(elf)
        defaults_owner(elf)
        tx_owner(elf)
        sections = sorted((s for s in elf.sections if s['flags'] & 2 and s['size'] and s['type'] != 8),
                          key=lambda s: s['address'])
        position, data = 0x8000, bytearray()
        for s in sections:
            need(s['address'] == position and s['type'] == 1, 'continuous file-backed full diagnostic')
            data.extend(elf.data(s))
            position += s['size']
        need(position == 0x1ac00 and len(data) == 76800
             and sha(data) == '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667',
             'full candidate digest retained')
        need(bytes(data) == (folder / ('NOT-FLASH-VALIDATED-v4160-source-' + mode + '.bin')).read_bytes(),
             'assembled candidate equals actual linked sections')
        need(bytes(data) == (conditional / ('NOT-FLASH-VALIDATED-conditional-link-' + mode + '.bin')).read_bytes(),
             'conditional binary readback matches')
        diff = [0x8000 + i for i, (a, b) in enumerate(zip(data, original)) if a != b]
        need(not diff and bytes(data) == original, 'all76800 original bytes equal')
        need(not any((conditional / (prefix + mode + '.elf')).exists()
                     for prefix in ('STRICT-', 'MISSING-CODE-', 'MISSING-DEFAULTS-')), 'no strict/negative link artifact')
        modes.append({'mode': mode, 'bytes': len(data), 'sha256': sha(data), 'original_different_bytes': len(diff),
                      'remaining_strict_ROM_provider': 'tsl9_boot_resident_40000', 'defaults_is_section_backed': True})
    return {'passed': True, 'modes': modes, 'conditional_DATA_aliases': 3,
            'hardware_validated': False, 'flashable_proved': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--build-root', type=Path, required=True)
    parser.add_argument('--original', type=Path, required=True)
    parser.add_argument('--write-receipt', type=Path)
    parser.add_argument('--candidate-root', type=Path)
    args = parser.parse_args()
    result = audit(args.build_root, args.original.read_bytes())
    if args.candidate_root:
        result['full_candidate'] = audit_full(args.candidate_root, args.original.read_bytes())
    if args.write_receipt:
        with args.write_receipt.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
