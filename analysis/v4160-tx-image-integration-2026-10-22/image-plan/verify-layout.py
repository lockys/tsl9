#!/usr/bin/env python3
"""Read-only BIN layout and candidate-BOOT shape checks; no OTA transport."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ORIGINAL = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BOOT = '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'
START, END, IMAGE_BYTES = 0x8A56 - 0x8000, 0x8B6E - 0x8000, 76800
# Data-only source anchors from the prior source-bound ID2580 review.
# They authenticate selected operands, not the installed BOOT or whole behavior.
ANCHORS = {
    0x2202: '83c7b108', 0x2208: '93072040', 0x220C: 'e39bf6fc',
    0x2210: '83471600', 0x2214: '03440600', 0x2218: '3787fff7',
    0x222A: 'b7070200', 0x222E: '93870702', 0x2238: 'e167',
    0x223C: '938707f0', 0x2240: 'e3e1e7fa', 0x25F4: '83c70700',
    0x25F8: '1307f006', 0x25FC: '6307f700',
}


def need(value, message):
    if not value:
        raise ValueError(message)


def H(payload):
    return hashlib.sha256(payload).hexdigest()


def boot_anchors(raw):
    for pc, value in ANCHORS.items():
        expected = bytes.fromhex(value)
        need(raw[pc - 0x1000:pc - 0x1000 + len(expected)] == expected,
             'selected BOOT source operand changed at ' + hex(pc))


def layout(original, candidate):
    need(len(original) == len(candidate) == IMAGE_BYTES, 'exact complete 76800-byte extent')
    need(candidate[:START] == original[:START] and candidate[END:] == original[END:],
         'every byte outside TX region remains original')
    need(candidate[0] == 0x6F, 'candidate retains the selected weak APP first-byte condition')
    need(len(candidate) % 1024 == 0, 'no implicit page padding')
    pages = []
    for index in range(len(candidate) // 1024):
        # This is the inherited selected-BOOT software formula, not ISA evaluation.
        offset = index * 1024
        need(offset <= 0x17F00 and index <= 95, 'selected candidate-BOOT numeric page bound')
        block = candidate[offset:offset + 1024]
        prefix = index.to_bytes(2, 'big')
        need(len(block) == 1024 and len(prefix + block) == 1026, 'exact page-data and prefix extents')
        pages.append({'index': index, 'file_offset': offset,
                      'software_alias_address': 0x08008000 + offset,
                      'data_sha256': H(block),
                      'index_prefixed_data_sum16': sum(prefix + block) & 65535})
    changed = [i for i, (a, b) in enumerate(zip(original, candidate)) if a != b]
    return {'candidate_bytes': len(candidate), 'candidate_sha256': H(candidate),
            'changed_bytes': len(changed), 'changed_file_offsets': changed,
            'permitted_change_file_range': [START, END],
            'outside_TX_bytes_identical': True, 'APP_first_byte': candidate[0],
            'page_data_bytes': 1024, 'index_prefixed_page_bytes': 1026,
            'page_count': len(pages), 'page_range': [0, len(pages) - 1],
            'software_alias_range': [0x08008000, 0x08008000 + len(candidate)],
            'pages': pages}


def controls(original, candidate, boot):
    probes = []
    for name, offset in [('first_byte_outside_TX', 0), ('tail_byte_outside_TX', len(candidate) - 1)]:
        changed = bytearray(candidate)
        changed[offset] ^= 1
        probes.append((name, lambda data=bytes(changed): layout(original, data)))
    probes.extend([('missing_tail_byte', lambda: layout(original, candidate[:-1])),
                   ('added_padding_byte', lambda: layout(original, candidate + b'\0'))])
    changed = bytearray(boot)
    changed[0x25F8 - 0x1000 + 3] ^= 1
    probes.append(('BOOT_firstbyte_operand', lambda: boot_anchors(bytes(changed))))
    out = []
    for name, check in probes:
        try:
            check()
        except ValueError as error:
            out.append({'name': name, 'rejected': True, 'reason': str(error)})
        else:
            raise ValueError('layout counterexample was admitted: ' + name)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--boot', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    original, candidate, boot = (p.read_bytes() for p in (args.original, args.candidate, args.boot))
    need(H(original) == ORIGINAL and H(boot) == BOOT, 'authenticated original/selected BOOT inputs')
    boot_anchors(boot)
    result = {'schema': 'TSL9-full-TX-image-local-layout-constraints-v1',
              'local_shape_constraints_passed': True, 'layout': layout(original, candidate),
              'inputs': {name: {'path': str(path.resolve()), 'bytes': len(data), 'sha256': H(data)}
                         for name, path, data in [('original', args.original, original),
                                                   ('candidate', args.candidate, candidate),
                                                   ('selected_BOOT', args.boot, boot)]},
              'runner_sha256': H(Path(__file__).read_bytes()),
              'raw_byte_counterexamples': controls(original, candidate, boot),
              'BOOT_source_anchors_checked': len(ANCHORS), 'selected_BOOT_sha256': BOOT,
              'inherited_BOOT_contract_source': 'v4160-ota-handoff-2026-10-21/boot-acceptance',
              'inherited_facts_sha256': 'af0d7d352758bf3f2a83080f30ffd20fed2293aef71d83f350781b64888aa8e2',
              'inherited_source_map_sha256': '77c9a864635bceb85f4ab283013ed8e8634a69dd566d0dff2dd23bc15f463d8b',
              'whole_BOOT_semantics_rederived': False, 'source_provider_provenance_proved_here': False,
              'complete_OTA_packet_or_identity_created': False, 'physical_flash_alias_proved': False,
              'image_CRC_or_signature_policy_proved': False,
              'installed_BOOT_identified': False, 'resident_ROM_contract_proved': False,
              'hardware_OTA_compatibility_proved': False, 'RV32_execution': False,
              'ISA_emulation': False, 'network': False, 'hardware': False}
    paths = [args.original.resolve(), args.candidate.resolve(), args.boot.resolve()]
    need(not args.receipt.exists() and args.receipt.resolve() not in paths, 'create-only distinct receipt')
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    with args.receipt.open('xb') as stream:
        stream.write((json.dumps(result, indent=2) + '\n').encode())
    print(json.dumps({'local_shape_constraints_passed': True, 'candidate_bytes': len(candidate),
                      'changed_bytes': result['layout']['changed_bytes'],
                      'pages': result['layout']['page_count'], 'counterexamples_rejected': 5,
                      'source_provenance_checked_here': False, 'hardware_OTA_proved': False,
                      'receipt': str(args.receipt), 'receipt_sha256': H(args.receipt.read_bytes())}))


if __name__ == '__main__':
    main()
