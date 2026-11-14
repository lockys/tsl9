#!/usr/bin/env python3
"""Bounded static fingerprints of five repository inputs; never executes them."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PINS = {
    'src/source-build-manifest.json': '466883524eca536c88653bce14057ec68c8c94d2c56368e185f1c2116abaf739',
    'src/compact-layout.json': 'af2aec2d6b88b40c72c4f7ddc1c696630ac65f25462d3173c18d53d140896b4b',
    'src/native/receive/state_events.c': 'c33e586aa7fd0eea2aef5367f3408675aa4615fc5e2d50d2243cc7a3350d55cf',
    'src/native/receive/state_leaf_reads.c': '28678f21b07c71613fe5f7b0f3e4f8a69d2b732a98e98d9d9be125653c2f7487',
    'scripts/verify-source-aggregate.py': 'e6fd9bb60f2414fe7a60f25d3e751c0d459978a25487c234b926ce4248674a37',
}
EVENT = 'src/native/receive/state_events.c'
LEAF = 'src/native/receive/state_leaf_reads.c'
AGG = 'scripts/verify-source-aggregate.py'
MANIFEST = 'src/source-build-manifest.json'
LAYOUT = 'src/compact-layout.json'
ALIAS = 'tsl9_events_external_d472'
TARGET = 'tsl9_state_leaf_entry_d472'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def expected_profile(registers, cpp):
    flags = ['--target=riscv32-unknown-elf', '-march=rv32imac_zicsr', '-mabi=ilp32', '-Oz', '-mllvm', '-enable-machine-outliner=never', '-ffreestanding', '-fno-builtin', '-fno-stack-protector', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables', '-mno-relax', '-ffunction-sections', '-fdata-sections', '-Wall', '-Wextra', '-Werror', '-x']
    flags += ['c++', '-std=c++17', '-fno-exceptions'] if cpp else ['c', '-std=c11']
    return flags + [f'-ffixed-x{i}' for i in registers]


def audit(root=ROOT, pins=PINS):
    data = {}
    for path, digest in pins.items():
        raw = (root / path).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == digest, 'hash mismatch: ' + path)
        data[path] = raw.decode('utf-8')
    manifest = json.loads(data[MANIFEST])
    for name, path, profile, regs in [
        ('state-events', EVENT, 'ring-bank', [1,2,3,4,5,7,8,9,*range(18,28),29,30,31]),
        ('state-leaf-reads', LEAF, 'queue-consumer-a0-a5', [*range(1,10),*range(16,32)]),
    ]:
        units = [u for u in manifest['native_units'] if u.get('name') == name or u.get('curated_unit') == path]
        require(units == [{'curated_unit': path, 'name': name, 'profile': profile}], 'unit profile: ' + name)
        entries = [f for f in manifest['files'] if f.get('destination') == path]
        require(entries == [{'destination': path, 'sha256': pins[path]}], 'manifest file pin: ' + name)
        require(manifest['code_profiles'][profile] == {lang: expected_profile(regs, lang == 'cpp') for lang in ('c', 'cpp')}, 'flags: ' + profile)
    require(json.loads(data[LAYOUT])['candidate_aliases'].get(ALIAS) == TARGET, 'alias map')
    require(data[EVENT].count('.reloc .-4, R_RISCV_JAL, ' + ALIAS) == 1, 'event relocation text')
    require(data[EVENT].count('jal ra, .Levent_control_13a54') == 1, 'event jal text')
    require(data[LEAF].count('REGION void ' + TARGET + '(void)') == 1, 'leaf symbol text')
    aggregate = data[AGG]
    for fragment in ["aliases = dict(compact['candidate_aliases']) if compact else {}", "*['--defsym=' + k + '=' + v for k, v in aliases.items()]", "symbols[k]['index'] not in (0, 0xfff1)", "symbols[k]['index'] == symbols[v]['index']", "symbols[k]['value'] == symbols[v]['value']", 'remaining != expected']:
        require(aggregate.count(fragment) == 1, 'aggregate text: ' + fragment)
    return {'passed': True, 'scope': 'five pinned files; textual fingerprints only'}


if __name__ == '__main__':
    try:
        print(json.dumps(audit(), sort_keys=True))
    except (OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
        print('FAIL: ' + str(exc), file=sys.stderr)
        sys.exit(1)
