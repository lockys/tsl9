#!/usr/bin/env python3
"""Offline verification of pinned record-helper BIN windows and source inventory."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
SPEC_SHA = 'f658349a73f7b246cbb037fc32185afbd12773cf2fa1f924eafbf6687a081d44'
SOURCE_SHA = 'deebd11bf4d9f852eade96fb581004ae2edbbbc14e3fbd11c5811bcd64e9e2f6'
IMAGE_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BASE, LENGTH = 0x8000, 76800
B0 = 'e3f6cec8c02b5619561c69f571f2b440db3d1b264b672e0f7520483a03dcf7eb'
SPEC_PATH = ROOT / 'experiments/tsl9-record-helpers/spec-v1.json'
SOURCE_PATH = ROOT / 'experiments/tsl9-record-helpers/src/record_helpers.v1.c'
BIN_PATH = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pin(data, expected, label):
    require(sha(data) == expected, label + ' SHA-256 mismatch')


def parse_spec(data):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=unique)


def validate_windows(regions, image, base):
    require(type(base) is int and base >= 0 and type(image) is bytes, 'invalid image/base')
    require(type(regions) is list and regions, 'regions must be a nonempty list')
    names, ordered = set(), []
    for r in regions:
        require(type(r) is dict, 'region must be an object')
        name, start, end, size, digest = (r.get(k) for k in ('name', 'start', 'end', 'bytes', 'original_sha256'))
        require(type(name) is str and re.fullmatch(r'[A-Za-z0-9_]+', name) is not None, 'invalid name')
        require(name not in names, 'duplicate name: ' + name)
        names.add(name)
        require(all(type(x) is int for x in (start, end, size)), 'invalid integer: ' + name)
        require(base <= start < end <= base + len(image) and start % 2 == end % 2 == 0 and size == end - start, 'invalid bounds/size: ' + name)
        suffix = re.search(r'_([0-9a-fA-F]+)$', name)
        require(suffix is not None and int(suffix.group(1), 16) == start, 'invalid suffix: ' + name)
        require(type(digest) is str and re.fullmatch(r'[0-9a-f]{64}', digest) is not None, 'invalid hash: ' + name)
        ordered.append(r)
    ordered.sort(key=lambda r: r['start'])
    require(all(a['end'] <= b['start'] for a, b in zip(ordered, ordered[1:])), 'overlapping windows')
    for r in ordered:
        require(sha(image[r['start']-base:r['end']-base]) == r['original_sha256'], 'slice SHA-256 mismatch: ' + r['name'])
    return ordered


def source_inventory(source, regions):
    # Ignore comments, quoted literals and preprocessing directives; reject any
    # remaining REGION token that is not a complete function definition.
    text = source.decode('utf-8')
    text = re.sub(r'/\*[\s\S]*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', ' ', text)
    text = re.sub(r'(?m)^\s*#[^\n]*', '', text)
    tokens = re.findall(r'\bREGION\b', text)
    names = re.findall(r'\bREGION\s+void\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(\s*void\s*\)\s*\{', text)
    require(len(tokens) == len(names) and len(names) == len(set(names)), 'invalid or duplicate source REGION')
    require(set(names) == {r['name'] for r in regions}, 'source REGION inventory mismatch')
    return names


def summary(regions):
    groups = []
    for r in regions:
        if groups and groups[-1][1] == r['start']:
            groups[-1][1] = r['end']
        else:
            groups.append([r['start'], r['end']])
    return {'regions': len(regions), 'bytes': sum(r['bytes'] for r in regions),
            'min_start': groups[0][0], 'max_end_exclusive': groups[-1][1],
            'adjacent_groups': groups, 'gaps': [[a[1], b[0]] for a, b in zip(groups, groups[1:])]}


def validate_b0(regions, image, base):
    require(type(regions) is list and type(image) is bytes and type(base) is int and base >= 0, 'invalid b0b0 inputs')
    require(all(type(r) is dict for r in regions), 'invalid b0b0 regions')
    matches = [r for r in regions if r.get('name') == 'tsl9_record_dispatch_provider_b0b0']
    require(len(matches) == 1, 'b0b0 missing or duplicate')
    r = matches[0]
    require(all(type(r.get(k)) is int for k in ('start', 'end', 'bytes')) and
            r['start'] == 0xb0b0 and r['end'] == 0xb0ba and r['bytes'] == 10 and
            r.get('original_sha256') == B0, 'b0b0 reference mismatch')
    offset = 0xb0b0 - base
    require(offset >= 0 and image[offset:offset+10].hex() == '97170020a38da7e28280', 'b0b0 bytes mismatch')


def verify(spec, source, image):
    pin(spec, SPEC_SHA, 'spec')
    pin(source, SOURCE_SHA, 'source')
    require(len(image) == LENGTH, 'image length mismatch')
    # Compare each window independently before checking the whole-image pin.
    regions = validate_windows(parse_spec(spec)['regions'], image, BASE)
    source_inventory(source, regions)
    validate_b0(regions, image, BASE)
    pin(image, IMAGE_SHA, 'image')
    return summary(regions)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', type=Path, default=SPEC_PATH, help='exact pinned spec')
    parser.add_argument('--source', type=Path, default=SOURCE_PATH, help='exact pinned source')
    parser.add_argument('--bin', type=Path, default=BIN_PATH)
    args = parser.parse_args()
    result = verify(args.spec.read_bytes(), args.source.read_bytes(), args.bin.read_bytes())
    print(json.dumps({'passed': True, 'base': BASE, **result}, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, UnicodeError) as exc:
        print('verification failed: ' + str(exc), file=sys.stderr)
        sys.exit(1)
