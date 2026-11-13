#!/usr/bin/env python3
"""Pinned offline byte-pattern scan, not a disassembler or call-graph builder."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = 0x8000
TARGET = 0x105c4
BIN = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
PINS = {
    'src/source-build-manifest.json': '466883524eca536c88653bce14057ec68c8c94d2c56368e185f1c2116abaf739',
    'src/native/receive/feature_state_records.c': '19a1c39ee7831f42960454d02393512520c425ea1ad90f9e08b0f8d4e3b32db3',
    'experiments/tsl9-feature-state-records/spec-v1.json': '4e04e3fdb4bf8f0d6bae85eb8f7f21071b800ea72719d9e45fa62083827aa893',
    'experiments/v4160-new-leaf-turn/leaf.c': 'e358a04a1c0d57589107315751ac0daf33cad9c53e104da80a7598da983396ff',
}
BIN_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
SYMBOL = 'tsl9_feature_state_records_provider_105c4'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pinned(data, digest, name):
    require(hashlib.sha256(data).hexdigest() == digest, name + ' hash mismatch')
    return data


def sign(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def jal(word, pc):
    if word & 0x7f != 0x6f:
        return None
    imm = (((word >> 31) & 1) << 20 | ((word >> 12) & 255) << 12 |
           ((word >> 20) & 1) << 11 | ((word >> 21) & 1023) << 1)
    delta = sign(imm, 21)
    return ((word >> 7) & 31, delta, (pc + delta) & 0xffffffff)


def cjal(half, pc):
    # RV32C only: same encoding is C.ADDIW on RV64C.
    if half & 0xe003 != 0x2001:
        return None
    imm = (((half >> 12) & 1) << 11 | ((half >> 11) & 1) << 4 |
           ((half >> 9) & 3) << 8 | ((half >> 8) & 1) << 10 |
           ((half >> 7) & 1) << 6 | ((half >> 6) & 1) << 7 |
           ((half >> 3) & 7) << 1 | ((half >> 2) & 1) << 5)
    delta = sign(imm, 12)
    return (1, delta, (pc + delta) & 0xffffffff)


def auipc_addi(raw, pc):
    require(len(raw) == 8, 'pair length')
    u = int.from_bytes(raw[:4], 'little')
    i = int.from_bytes(raw[4:], 'little')
    rd = (u >> 7) & 31
    require(u & 0x7f == 0x17 and i & 0x707f == 0x13 and rd != 0 and
            (i >> 7) & 31 == rd and (i >> 15) & 31 == rd, 'pair fields')
    return rd, (pc + sign(u & 0xfffff000, 32) + sign(i >> 20, 12)) & 0xffffffff


def scan(data, base=BASE, target=TARGET):
    result = []
    counts = {'JAL': 0, 'C.JAL/RV32': 0}
    # Every byte start, including odd, overlapping, and data windows.
    for width, kind, decode in ((4, 'JAL', jal), (2, 'C.JAL/RV32', cjal)):
        for off in range(max(0, len(data) - width + 1)):
            raw = data[off:off + width]
            pc = (base + off) & 0xffffffff
            counts[kind] += 1
            decoded = decode(int.from_bytes(raw, 'little'), pc)
            if decoded is not None and decoded[2] == target:
                rd, delta, dest = decoded
                result.append({'offset': off, 'pc': pc, 'bytes': raw.hex(),
                               'kind': kind, 'rd': rd, 'delta': delta,
                               'target': dest, 'alignment': 'odd' if pc & 1 else 'halfword',
                               'classification': 'raw pattern; instruction boundary and reachability unproven'})
    return sorted(result, key=lambda x: (x['offset'], x['kind'])), counts


def verify_evidence(data, snapshots):
    require(len(data) == 76800, 'BIN length')
    pinned(data, BIN_SHA, 'BIN')
    for name, digest in PINS.items():
        pinned(snapshots[name], digest, name)
    path = 'src/native/receive/feature_state_records.c'
    owner = snapshots[path].decode('utf-8')
    manifest = json.loads(snapshots['src/source-build-manifest.json'])
    spec = json.loads(snapshots['experiments/tsl9-feature-state-records/spec-v1.json'])
    require([x['sha256'] for x in manifest['files'] if x['destination'] == path] == [PINS[path]], 'manifest owner')
    require(any(x.get('curated_unit') == path and x.get('name') == 'feature-state-records' and x.get('profile') == 'queue-consumer-a0-a5' for x in manifest['native_units']), 'manifest unit')
    regions = [x for x in spec['regions'] if x['name'] == SYMBOL]
    leaf = data[TARGET - BASE:TARGET - BASE + 12]
    require(len(regions) == 1 and regions[0]['start'] == TARGET and regions[0]['end'] == TARGET + 12 and regions[0]['bytes'] == 12 and regions[0]['original_sha256'] == hashlib.sha256(leaf).hexdigest(), 'spec region')
    require(leaf.hex() == '034535007115133515008280', 'leaf bytes')
    pairs = [x for x in spec['PC_relative_pairs'] if x.get('target') == SYMBOL]
    require([(x['PC'], x['target_PC']) for x in pairs] == [(0x1094c, TARGET), (0x10be4, TARGET)], 'spec incoming pairs')
    needle = 'R_RISCV_PCREL_HI20,' + SYMBOL
    require(owner.count(needle) == 2, 'owner relocation count')
    for pc, rd in ((0x1094c, 10), (0x10be4, 13)):
        require(auipc_addi(data[pc-BASE:pc-BASE+8], pc) == (rd, TARGET), 'original pair target')
        label = '.Lfeature_state_records_literal_%x' % pc
        require(label + ':\\n.option push\\n.option norvc\\nauipc ' in owner, 'owner HI anchor')
        pos = owner.index(label + ':\\n')
        line = owner[pos:owner.index('\n', pos)]
        require(needle in line and 'R_RISCV_PCREL_LO12_I,' + label in line, 'owner HI/LO pair')
    for pc, expected in WINDOWS.items():
        require(data[pc-BASE:pc-BASE+len(bytes.fromhex(expected))].hex() == expected, 'window at %#x' % pc)
    return pairs


WINDOWS = {
    0x105c4: '034535007115133515008280',
    0x10944: '411122c4aa852a8417050000130585c706c6eff07fee',
    0x1083c: '4111aa872e8522c406c68297',
    0x10bbe: '6ff09fc0',
    0x10bc2: '411122c4970600009386869a2a840946a9451385611406c6eff0dfbe22872244b240970600009386069e0d46a945138571144101e1b7',
    0x107c6: '011122cc2a843a8526ca06ce2ec6b2848296',
}


def main():
    data = BIN.read_bytes()
    snapshots = {name: (ROOT / name).read_bytes() for name in PINS}
    pairs = verify_evidence(data, snapshots)
    hits, counts = scan(data)
    print(json.dumps({'range': [BASE, BASE + len(data)], 'bin_sha256': BIN_SHA,
                      'windows': counts,
                      'formal_incoming_pairs': pairs, 'raw_hits': hits}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, UnicodeError) as exc:
        print('FAIL: ' + str(exc), file=sys.stderr)
        sys.exit(1)
