#!/usr/bin/env python3
"""Verify only the direct references enumerated by the pinned V4.1.60 spec."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = ROOT / 'experiments/tsl9-record-helpers/spec-v1.json'
BIN_PATH = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SPEC_SHA = 'f658349a73f7b246cbb037fc32185afbd12773cf2fa1f924eafbf6687a081d44'
IMAGE_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BASE, LENGTH = 0x8000, 76800


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def parse_spec(data):
    def unique(items):
        out = {}
        for key, value in items:
            require(key not in out, 'duplicate JSON key: ' + key)
            out[key] = value
        return out
    return json.loads(data, object_pairs_hook=unique)


def integer(value, label, low=0, high=0xffffffff):
    require(type(value) is int and low <= value <= high, 'invalid ' + label)
    return value


def name(value):
    require(type(value) is str and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', value) is not None, 'invalid name')
    return value


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def address(pc, displacement):
    result = pc + displacement
    require(0 <= result <= 0xffffffff, 'target address overflow')
    return result


def decode_control(raw, pc, kind):
    integer(pc, 'PC'); integer(kind, 'type')
    require(pc % 2 == 0 and type(raw) is bytes, 'unaligned PC or invalid bytes')
    if kind in (16, 17):
        require(len(raw) == 4, 'control width')
        w = int.from_bytes(raw, 'little')
        require(w & 3 == 3 and w & 0x1f != 0x1f, 'not a 32-bit instruction')
        if kind == 17:
            require(w & 0x7f == 0x6f and (w >> 7) & 31 in (0, 1), 'expected JAL with x0 or x1 link')
            imm = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
            return address(pc, signed(imm, 21))
        require(w & 0x7f == 0x63 and (w >> 12) & 7 in (0, 1, 4, 5, 6, 7), 'expected valid branch')
        imm = ((w >> 31) << 12) | (((w >> 7) & 1) << 11) | (((w >> 25) & 63) << 5) | (((w >> 8) & 15) << 1)
        return address(pc, signed(imm, 13))
    require(kind in (44, 45) and len(raw) == 2, 'unsupported type or control width')
    w = int.from_bytes(raw, 'little')
    require(w & 3 == 1, 'expected compressed quadrant 1')
    funct = w >> 13
    if kind == 44:
        require(funct in (6, 7), 'expected C.BEQZ/C.BNEZ')
        imm = (((w >> 12) & 1) << 8) | (((w >> 10) & 3) << 3) | (((w >> 5) & 3) << 6) | (((w >> 3) & 3) << 1) | (((w >> 2) & 1) << 5)
        return address(pc, signed(imm, 9))
    require(funct == 5, 'expected C.J (not C.JAL)')
    imm = (((w >> 12) & 1) << 11) | (((w >> 11) & 1) << 4) | (((w >> 9) & 3) << 8) | (((w >> 8) & 1) << 10) | (((w >> 7) & 1) << 6) | (((w >> 6) & 1) << 7) | (((w >> 3) & 7) << 1) | (((w >> 2) & 1) << 5)
    return address(pc, signed(imm, 12))


def decode_pair(raw, pc):
    integer(pc, 'PC')
    require(pc % 2 == 0 and type(raw) is bytes and len(raw) == 8, 'pair width/PC')
    a, b = int.from_bytes(raw[:4], 'little'), int.from_bytes(raw[4:], 'little')
    require(a & 0x7f == 0x17 and b & 0x707f == 0x13, 'expected AUIPC/ADDI')
    rd, dest, rs1 = (a >> 7) & 31, (b >> 7) & 31, (b >> 15) & 31
    require(rd != 0 and dest == rd and rs1 == rd, 'broken AUIPC/ADDI register chain')
    return address(pc, signed(a & 0xfffff000, 32) + signed(b >> 20, 12))


def validate_regions(regions, image, base):
    integer(base, 'base')
    require(type(image) is bytes and base + len(image) <= 0x100000000, 'invalid image bounds')
    require(type(regions) is list and regions, 'invalid regions')
    by_name = {}
    for r in regions:
        require(type(r) is dict, 'invalid region')
        n = name(r.get('name'))
        require(n not in by_name, 'duplicate region: ' + n)
        start, end, size = (integer(r.get(k), k) for k in ('start', 'end', 'bytes'))
        require(base <= start < end <= base + len(image) and not (start | end) & 1 and size == end - start, 'region bounds: ' + n)
        h = r.get('original_sha256')
        require(type(h) is str and re.fullmatch(r'[0-9a-f]{64}', h) is not None, 'invalid region hash')
        require(digest(image[start-base:end-base]) == h, 'region hash: ' + n)
        by_name[n] = r
    ordered = sorted(by_name.values(), key=lambda r: r['start'])
    require(all(a['end'] <= b['start'] for a, b in zip(ordered, ordered[1:])), 'overlapping regions')
    # Only each adjacent group's first start is assumed to be a boundary.
    # Walk continuously through the group, requiring every region end to be one.
    groups, starts = [], set()
    for r in ordered:
        if not groups or groups[-1][1] != r['start']:
            groups.append([r['start'], r['start']])
        cursor = groups[-1][1]
        while cursor < r['end']:
            raw = image[cursor-base:cursor-base+2]
            require(len(raw) == 2, 'truncated instruction at ' + hex(cursor))
            half = int.from_bytes(raw, 'little')
            step = 2 if half & 3 != 3 else 4
            require(step == 2 or half & 0x1f != 0x1f, 'unsupported instruction width at ' + hex(cursor))
            require(cursor + step <= r['end'], 'instruction crosses region boundary or is truncated at ' + hex(cursor))
            starts.add(cursor)
            cursor += step
        groups[-1][1] = cursor
    return by_name, groups, starts


def validate_references(spec, image, base, expected_counts=None):
    require(type(spec) is dict, 'invalid spec')
    regions, groups, starts = validate_regions(spec.get('regions'), image, base)
    controls, pairs, undefined = (spec.get(k) for k in ('controls', 'PC_relative_pairs', 'undefined'))
    require(all(type(x) is list for x in (controls, pairs, undefined)), 'invalid reference lists')
    if expected_counts is not None:
        require((len(regions), len(controls), len(pairs), len(undefined)) == expected_counts, 'inventory count mismatch')
    names = [name(n) for n in undefined]
    require(len(names) == len(set(names)) and not set(names) & regions.keys(), 'duplicate or internal undefined')
    externals, addresses, occupied, evidence = {}, {}, set(), []
    for is_pair, entries in ((False, controls), (True, pairs)):
        for entry in entries:
            require(type(entry) is dict, 'invalid reference entry')
            expected = {'owner', 'offset', 'PC', 'target', 'target_PC'} | ({'reference_kind', 'data_contents_provided'} if is_pair else {'size', 'type'})
            require(set(entry) == expected, 'invalid reference fields')
            owner, target = name(entry['owner']), name(entry['target'])
            require(owner in regions, 'unknown owner: ' + owner)
            r = regions[owner]
            offset, pc, target_pc = (integer(entry[k], k) for k in ('offset', 'PC', 'target_PC'))
            if is_pair:
                require(entry['reference_kind'] in ('callback-address', 'opaque-static-data-address') and type(entry['data_contents_provided']) is bool and not entry['data_contents_provided'], 'invalid pair metadata')
                width = 8
            else:
                width = integer(entry['size'], 'size')
                integer(entry['type'], 'type')
            require(pc == r['start'] + offset and pc % 2 == 0 and r['start'] <= pc and pc + width <= r['end'], 'reference PC/bounds: ' + owner)
            require(pc in starts, 'reference not at instruction boundary')
            span = set(range(pc, pc + width))
            require(not occupied & span, 'duplicate or overlapping reference')
            occupied.update(span)
            raw = image[pc-base:pc-base+width]
            actual = decode_pair(raw, pc) if is_pair else decode_control(raw, pc, entry['type'])
            require(actual == target_pc, 'decoded target mismatch at ' + hex(pc))
            require(target not in addresses or addresses[target] == actual, 'inconsistent target address: ' + target)
            addresses[target] = actual
            if target in regions:
                require(actual == regions[target]['start'], 'internal target is not region start')
            else:
                require(target in names, 'target missing from undefined: ' + target)
                require(not any(r['start'] <= actual < r['end'] for r in regions.values()), 'external target inside region')
                externals.setdefault(target, []).append(pc)
            evidence.append({'owner': owner, 'PC': pc, 'bytes': raw.hex(), 'kind': entry['reference_kind'] if is_pair else entry['type'], 'target': target, 'decoded_target': actual})
    require(set(externals) == set(names), 'undefined/reference set mismatch')
    require(len(set(addresses.values())) == len(addresses), 'target address collision')
    return {'assumed_boundary_groups': groups, 'references': evidence, 'external_targets': {n: {'address': addresses[n], 'count': len(externals[n]), 'reference_PCs': externals[n]} for n in sorted(externals)}}


def verify(spec_bytes, image):
    require(type(spec_bytes) is bytes and digest(spec_bytes) == SPEC_SHA, 'spec SHA-256 mismatch')
    require(type(image) is bytes and len(image) == LENGTH and digest(image) == IMAGE_SHA, 'image length/SHA-256 mismatch')
    spec = parse_spec(spec_bytes)
    distribution = {(16, 4): 6, (17, 4): 26, (44, 2): 14, (45, 2): 5}
    counts = {}
    for ref in spec['controls']:
        integer(ref['type'], 'type'); integer(ref['size'], 'size')
        key = (ref['type'], ref['size'])
        counts[key] = counts.get(key, 0) + 1
    require(counts == distribution, 'control type/size distribution mismatch')
    result = validate_references(spec, image, BASE, (68, 51, 11, 18))
    require(len(result['assumed_boundary_groups']) == 8, 'region group count mismatch')
    jal_rd = {'ra_x1_call': 0, 'x0_jump_no_link': 0}
    for ref in result['references']:
        if ref['kind'] == 17:
            rd = (int.from_bytes(bytes.fromhex(ref['bytes']), 'little') >> 7) & 31
            link = 'ra_x1_call' if rd == 1 else 'x0_jump_no_link'
            ref['link'] = link
            jal_rd[link] += 1
    require(jal_rd == {'ra_x1_call': 16, 'x0_jump_no_link': 10}, 'JAL link distribution mismatch')
    return {'passed': True, 'base': BASE, 'jal_rd': jal_rd, **result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', type=Path, default=SPEC_PATH)
    parser.add_argument('--bin', type=Path, default=BIN_PATH)
    args = parser.parse_args()
    print(json.dumps(verify(args.spec.read_bytes(), args.bin.read_bytes()), indent=2, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, TypeError, KeyError, OSError, UnicodeError) as exc:
        print('verification failed: ' + str(exc), file=sys.stderr)
        sys.exit(1)
