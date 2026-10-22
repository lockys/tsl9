"""Bounded literal-interior-reference inventory; never execute a target image."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent
PLAN_SEAL = '81912879ab740bff2055d518eac48f2191fad242ed782fc84cc7e3d0ea62169d'
EXPECTED = {
    'original': '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667',
    'previous_IRQ': '47f200dce24be25ac89d57922689da536259935e8615ba8195b10ca192895e1c',
    'eleven_function_candidate': 'de159bb345b27250a683e197dd84b04e51a7a7ed89315347395baaea53f68be1',
}
ALIASES = (0, 0x08000000)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def scan(data, owners):
    hits = []
    patterns = 0
    for owner in owners:
        for alias in ALIASES:
            for delta in range(1, owner['bytes']):
                target = alias + owner['originalVA'] + delta
                patterns += 1
                needle = struct.pack('<I', target)
                start = 0
                while True:
                    at = data.find(needle, start)
                    if at < 0:
                        break
                    hits.append(dict(carrier_offset=at, little_endian_value=target,
                                     owner=owner['name'], interior_offset=delta,
                                     numeric_alias=alias, carrier_alignment_mod4=at % 4))
                    start = at + 1
    return dict(patterns=patterns, carrier_offsets=max(0, len(data)-3), hits=hits)


def inspect(root, images):
    cases = (root/'analysis/v4160-flash-entry-order-2026-10-22',
             root/'apk-analysis/tsl9-v4160-flash-entry-order-2026-10-22')
    case = next((p for p in cases if p.is_dir()), None)
    need(case is not None, 'Explicit project contains the sealed entry-order plan')
    seal_path = case/'image-plan/seal.json'
    need(sha(seal_path.read_bytes()) == PLAN_SEAL, 'Exact sealed source plan')
    seal = json.loads(seal_path.read_text(encoding='utf8'))
    for item in seal['members']:
        member = (seal_path.parent/item['path']).resolve()
        need(member.is_relative_to(seal_path.parent.resolve()) and sha(member.read_bytes()) == item['sha256'], 'Exact source-plan member')
    plan = json.loads((case/'image-plan/report.json').read_text(encoding='utf8'))
    owners = plan['selected']
    need(len(owners) == 11 and sum(o['bytes'] for o in owners) == 526, 'Eleven exact original function extents')
    bounds = sorted((o['originalVA'], o['originalVA']+o['bytes']) for o in owners)
    need(all(a[1] <= b[0] for a, b in zip(bounds, bounds[1:])), 'Disjoint function ranges')
    actual = {}
    for role, path in images.items():
        data = path.read_bytes()
        need(len(data) == 76800 and sha(data) == EXPECTED[role], 'Exact admitted image '+role)
        actual[role] = dict(bytes=len(data), sha256=sha(data), **scan(data, owners))
    controls = []
    owner = owners[0]
    for alias in ALIASES:
        target = alias + owner['originalVA'] + 1
        for offset in (0, 1, 2, 3):
            data = b'\xff'*offset + struct.pack('<I', target) + b'\xff'*4
            result = scan(data, owners)
            need(any(h['carrier_offset'] == offset and h['little_endian_value'] == target for h in result['hits']), 'Detect synthetic aligned and unaligned literals')
            controls.append(dict(numeric_alias=alias, offset=offset, detected=True))
        entry = struct.pack('<I', alias + owner['originalVA'])
        need(not scan(entry, owners)['hits'], 'Entry addresses are not interior evidence')
        controls.append(dict(numeric_alias=alias, entry_excluded=True))
    return dict(schema='TSL9-bounded-literal-interior-inventory-v1', passed=True,
                plan_seal_sha256=PLAN_SEAL, functions=11, original_function_bytes=526,
                numeric_aliases_examined=list(ALIASES), aliases_prove_hardware_mapping=False,
                carrier='all byte offsets of each complete 76800-byte image',
                encoding='literal 32-bit little-endian value only', images=actual,
                synthetic_detector_controls=controls,
                no_literal_hits=all(not r['hits'] for r in actual.values()),
                computed_or_encoded_references_excluded=False, external_ROM_inspected=False,
                full_instruction_boundary_equivalence=False, pointwise_async_equivalence=False,
                target_execution=False, ISA_emulation=False, hardware=False, network=False,
                new_BIN=False, OTA_ready=False)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', required=True, type=Path)
    p.add_argument('--original', required=True, type=Path)
    p.add_argument('--previous', required=True, type=Path)
    p.add_argument('--candidate', required=True, type=Path)
    action = p.add_mutually_exclusive_group(required=True)
    action.add_argument('--write', action='store_true')
    action.add_argument('--check', action='store_true')
    a = p.parse_args()
    report = inspect(a.project_root.resolve(), dict(original=a.original.resolve(),
                     previous_IRQ=a.previous.resolve(), eleven_function_candidate=a.candidate.resolve()))
    payload = (json.dumps(report, indent=2)+'\n').encode('utf8')
    destination = HERE/'report.json'
    if a.write:
        with destination.open('xb') as output:
            output.write(payload)
    else:
        need(destination.read_bytes() == payload, 'Exact bounded inventory replay')
    print(json.dumps(dict(passed=True, image_count=3, patterns_per_image=1030,
                         offsets_per_image=76797, synthetic_controls=10,
                         literal_hits=sum(len(r['hits']) for r in report['images'].values()),
                         computed_references_or_ROM_proved_absent=False, OTA_ready=False)))
