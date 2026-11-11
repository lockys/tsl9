"""Cross-check sparse diagnostic inputs against the pinned original Intel HEX."""
import hashlib
import json
import runpy
from pathlib import Path

MAP_SHA = '96ff0490ccd196ee97655a80ed44ea2b1ceee53b84ca3bad8f8f74525031c0ba'

def validate(root, ref):
    check = runpy.run_path(str(root / 'analysis/v131-startup-source/check.py'))
    raw = (root / 'analysis/v131-startup-source/wchble_rom.hex').read_bytes()
    if hashlib.sha256(raw).hexdigest() != check['HEX_SHA']:
        raise ValueError('official HEX hash mismatch')
    mem = check['parse'](raw)
    raw_map = (ref / 'source-map.json').read_bytes()
    if hashlib.sha256(raw_map).hexdigest() != MAP_SHA:
        raise ValueError('Reference map changed')
    m = json.loads(raw_map)
    segments = m['segments']
    if not m['passed'] or len(segments) != 17:
        raise ValueError('Reference segments changed')
    covered = set()
    for s in segments:
        path = (ref / s['path']).resolve()
        start, end = s['start'], s['end_exclusive']
        if path.parent != ref or path.suffix != '.bin' or end - start != s['bytes'] or end <= start:
            raise ValueError('Invalid reference segment')
        addresses = set(range(start, end))
        if covered & addresses or not addresses <= mem.keys():
            raise ValueError('Reference overlaps or covers missing HEX bytes')
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != s['sha256'] or data != bytes(mem[p] for p in range(start, end)):
            raise ValueError('Reference segment differs from HEX')
        covered.update(addresses)
    if covered != mem.keys():
        raise ValueError('Reference coverage differs from HEX')
    if segments[0]['start'] != 0x40000 or segments[0]['end_exclusive'] != 0x6ea66 or segments[-1]['start'] != 0x6eaa4 or segments[-1]['end_exclusive'] != 0x6eb2c:
        raise ValueError('Reference extents changed')
    if [p for p in range(0x6eaa4, 0x6eb30) if p not in covered] != list(range(0x6eb2c, 0x6eb30)):
        raise ValueError('Startup source coverage changed')
    return segments
