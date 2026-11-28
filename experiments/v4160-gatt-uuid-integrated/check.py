"""Audit a fresh source-only selected build; never run firmware."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import struct

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


def audit(folder, original):
    support = runpy.run_path(str(ROOT / 'scripts/source-build-support.py'))
    manifest = support['metadata']()
    provenance = runpy.run_path(str(ROOT / 'scripts/verify-curated-source.py'))['metadata']()
    need(len(provenance['files']) == len(manifest['files']) == 174, 'complete registered source inventory')
    record = json.loads((folder / 'NOT-FLASHABLE-spans.json').read_bytes())
    need(len(record['outputs']) == 2 and record['candidate_bytes_read'] == 0
         and not record['excluded_read'] and not record['complete_firmware']
         and not record['flashable'], 'bounded source-only span receipt')
    mapping = json.loads((ROOT / 'src/compact-layout.json').read_bytes())
    need(sha(original) == '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667', 'original image identity')
    need(len(original) == 76800, 'original length')
    expected_ranges = [(0x8000, 0x14056), (0x14c8a, 0x1a69c), (0x1a6a0, 0x1ac00)]
    rows = []
    all_memory = []
    for mode, receipt in zip(('c', 'cpp'), record['outputs']):
        need(receipt['mode'] == mode, 'mode receipt order')
        expected_units = {u['name'] for u in manifest['native_units'] + manifest['native_data_units']}
        expected_units.update([manifest['window']['name'], manifest['opaque']['name']])
        objects = list((folder / 'build' / 'source' / mode).glob('*/unit.o'))
        need(len(objects) == 141 and {p.parent.name for p in objects} == expected_units,
             'all registered units have fresh output objects')
        elf = ELF(folder / 'build' / ('NOT-FLASHABLE-compact-source-layout-' + mode + '.elf'))
        diagnostic_header(elf)
        uuid_owner(elf)
        runpy.run_path(str(ROOT / 'scripts/relative_table_owner.py'))['check_relative_table_owner'](elf)
        spans = sorted((s for s in elf.sections if s['flags'] & 2 and s['size']), key=lambda s: s['address'])
        need(len(spans) == 6268, 'fresh selected section count')
        memory = {}
        for s in spans:
            start, end = s['address'], s['address'] + s['size']
            need(s['type'] == 1 and any(lo <= start < end <= hi for lo, hi in expected_ranges), 'permitted selected range')
            for i, byte in enumerate(elf.data(s)):
                need(start + i not in memory, 'no overlapping allocated bytes')
                memory[start + i] = byte
        need(len(memory) == 73672, 'selected byte count retained')
        payload = bytes(memory[p] for p in sorted(memory))
        need(sha(payload) == mapping['selected_linked_sha256'] == receipt['sha256'], 'unchanged selected linked bytes')
        binary = (folder / ('NOT-FLASHABLE-selected-spans-' + mode + '.bin')).read_bytes()
        need(binary == payload, 'span file equals fresh linked ELF bytes')
        need([(s['start'], s['end']) for s in receipt['spans']] == expected_ranges, 'exact selected spans')
        differences = [p for p, byte in memory.items() if byte != original[p - 0x8000]]
        need(len(differences) == 93 and all(0x8a56 <= p < 0x8b6e for p in differences), 'retain known 93-byte candidate TX difference only')
        need(bytes(memory[p] for p in (0x1ab44, 0x1ab45)) == original[0x12b44:0x12b46], 'UUID agrees with original bytes')
        unresolved = sorted({s['name'] for s in ELF(folder / 'build' / 'source' / ('NOT-FLASHABLE-candidate-aliases-' + mode + '.o')).symbols
                             if s['name'] and s['index'] == 0 and s['info'] >> 4 in (1, 2)})
        need(set(unresolved) == {'__tsl9v4160_data_2000b18c', 'tsl9_boot_resident_40000',
                                'tsl9_incoming_external_14056', 'tsl9_input_state_decoders_static_data_1ab48',
                                'tsl9_record_field_transitions_static_data_1a078',
                                'tsl9_registered_callbacks_static_data_1a638', 'tsl9_runtime_reset_stack_top',
                                'tsl9_settings_default_data_1a69c'},
             'source aggregate keeps exact eight dependencies before stack witness')
        need(not (folder / 'build' / ('STRICT-' + mode + '.elf')).exists(), 'strict link produced no firmware')
        rows.append({'mode': mode, 'selected_sections': len(spans), 'selected_bytes': len(memory),
                     'selected_sha256': sha(payload), 'original_differences': len(differences), 'unresolved_before_stack_witness': unresolved})
        all_memory.append(memory)
    need(all_memory[0] == all_memory[1], 'C11/C++17 identical original-coordinate bytes')
    paths = ['src/source-manifest.json', 'src/source-build-manifest.json', 'src/compact-layout.json',
             'src/native/receive/gatt_write_uuid.c', 'src/native/receive/opaque_allowed_gaps.c',
             'scripts/source-build-support.py', 'scripts/verify-source-aggregate.py',
             'scripts/build-compact-source-layout.py', 'scripts/build-source-spans.py',
             'scripts/relative_table_owner.py', 'experiments/v4160-gatt-uuid-source-extension/origin.c',
             'experiments/v4160-gatt-uuid-integrated/check.py', 'experiments/v4160-gatt-uuid-integrated/spec-v1.json']
    return {'passed': True, 'source_files': 174, 'CODE_units': 125, 'DATA_units': 14,
            'fresh_registered_objects_per_language': 141, 'modes': rows,
            'UUID_bytes_migrated_from_opaque': 2, 'selected_bytes_added': 0,
            'historical_objects_used_for_build': False, 'candidate_used_for_build': False,
            'new_flashable_BIN': False, 'target_executed': False,
            'inputs_sha256': {p: sha((ROOT / p).read_bytes()) for p in paths}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--build-root', type=Path, required=True)
    parser.add_argument('--original', type=Path, required=True)
    parser.add_argument('--write-receipt', type=Path)
    args = parser.parse_args()
    result = audit(args.build_root, args.original.read_bytes())
    if args.write_receipt:
        with args.write_receipt.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
