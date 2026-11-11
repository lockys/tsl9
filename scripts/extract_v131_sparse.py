#!/usr/bin/env python3
"""Derive offline diagnostic segments from the pinned official raw HEX."""
import argparse
import hashlib
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK = runpy.run_path(str(ROOT / 'analysis/v131-startup-source/check.py'))
COMMIT = 'ec059e0b18046b111ee850e44f105fcd095e775c'
SOURCE_PATH = 'EVT/EXAM/BLE/LIB/wchble_rom.hex'
BLOB = '13202d1678c9766117d787d98b4de55ed61fc571'


def derive(raw):
    if hashlib.sha256(raw).hexdigest() != CHECK['HEX_SHA']:
        raise ValueError('official HEX hash mismatch')
    if hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() != BLOB:
        raise ValueError('official git blob mismatch')
    mem = CHECK['parse'](raw)
    addresses = sorted(mem)
    spans = []
    for p in addresses:
        if not spans or p != spans[-1][1]:
            spans.append([p, p + 1])
        else:
            spans[-1][1] += 1
    if len(mem) != 191244 or len(spans) != 17 or spans[0] != [0x40000, 0x6ea66] or spans[-1] != [0x6eaa4, 0x6eb2c] or any(p in mem for p in range(0x6eb2c, 0x6eb30)):
        raise ValueError('unexpected sparse coverage')
    files = {}
    segments = []
    for start, end in spans:
        name = f'REFERENCE-CANDIDATE-ONLY-{start:08X}-{end:08X}.bin'
        data = bytes(mem[p] for p in range(start, end))
        files[name] = data
        segments.append({'path': name, 'start': start, 'end_exclusive': end,
                         'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    manifest = {'schema': 'v131-derived-sparse-v1', 'passed': True,
                'source': {'repository': 'https://github.com/openwch/ch32v20x',
                           'commit': COMMIT, 'path': SOURCE_PATH,
                           'sha256': CHECK['HEX_SHA'], 'git_blob_sha1': BLOB},
                'segments': segments}
    files['source-map.json'] = (json.dumps(manifest, indent=2) + '\n').encode('ascii')
    return files


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--hex', type=Path, required=True, help='existing raw official HEX; no download')
    p.add_argument('--out', type=Path, required=True, help='new directory outside project and source directory')
    a = p.parse_args()
    source = a.hex.resolve(strict=True)
    out = a.out.resolve()
    if out == ROOT or ROOT in out.parents or out == source.parent or source.parent in out.parents or out in source.parents:
        raise ValueError('output must be outside project and source directory')
    files = derive(source.read_bytes())
    out.mkdir(parents=True, exist_ok=False)
    for name, data in files.items():
        (out / name).write_bytes(data)
    print(f'Generated {len(files)-1} sparse segments in {out}; not flashable')


if __name__ == '__main__':
    main()
