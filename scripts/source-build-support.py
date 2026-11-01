"""Pinned source-tree-only inputs and compile profiles for diagnostic builds."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
PARSER = ROOT / 'src/native/tx_candidate/postpass/elf32.py'
MANIFEST = ROOT / 'src/source-build-manifest.json'
_manifest = None
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def metadata():
    global _manifest
    if sha(MANIFEST) != 'f47b61a3b38cd46ed2137d5b00d02e61f3f8a1211482e31bff301c5474e1e574':
        raise ValueError('Pinned source build manifest changed')
    data = json.loads(MANIFEST.read_text(encoding='utf-8'))
    if data['schema'] != 'tsl9-source-build-v1' or sha(PARSER) != '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141':
        raise ValueError('Source build schema or parser changed')
    files = data['files']
    actual = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'src').rglob('*') if p.is_file() and p.suffix in {'.c', '.h', '.cc', '.cpp', '.hpp'}}
    if len(files) != 172 or len({x['destination'] for x in files}) != len(files) or {x['destination'] for x in files} != actual:
        raise ValueError('Source inventory changed')
    for item in files:
        path = (ROOT / item['destination']).resolve()
        if not path.is_relative_to(ROOT / 'src') or sha(path) != item['sha256']:
            raise ValueError('Source hash changed: ' + item['destination'])
    if len(data['native_units']) != 125 or len(data['native_data_units']) != 13:
        raise ValueError('Source unit inventory changed')
    _manifest = data
    return data
def command(tools, unit, mode, variant, folder):
    if _manifest is None or variant != 'curated':
        raise ValueError('Only verified curated source is supported')
    source = ROOT / unit['curated_unit']
    return [tools['clang'], *_manifest['code_profiles'][unit['profile']][mode], '-c', '-MD', '-MF', folder / 'unit.d', '-MT', 'unit.o', source, '-o', folder / 'unit.o']
def data_flags(unit, mode):
    if _manifest is None:
        raise ValueError('Source metadata must be checked first')
    return _manifest['data_profiles'][unit['profile']][mode]
def dependencies(folder, variant, resource):
    if variant != 'curated':
        raise ValueError('Only curated include paths are supported')
    text = (folder / 'unit.d').read_text(encoding='utf-8').replace('\\\n', ' ')
    target, separator, tail = text.partition(':')
    if not separator or target != 'unit.o':
        raise ValueError('Unexpected dependency target')
    paths = {Path(re.sub(r'\\(.)', r'\1', token)).resolve() for token in re.findall(r'(?:\\.|[^\s])+', tail)}
    if not paths or not all(p.is_relative_to(ROOT / 'src') or p.is_relative_to(resource) for p in paths):
        raise ValueError('Unexpected source include')
    return {str(p): sha(p) for p in sorted(paths)}
