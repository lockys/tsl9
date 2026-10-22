"""Bounded source operand proof, without instruction execution."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
FW = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BINDING = '16d33830cd05b0fb49b4ecf576b1657cf4c6a5bedabd4ccc63dc73ef3ef1f551'


def need(v, message):
    if not v:
        raise ValueError(message)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_bytes())


def locate(root, name):
    p = root / name
    if name.startswith('analysis/') and not p.exists():
        p = root / ('apk-analysis/tsl9-' + name.removeprefix('analysis/'))
    elif name.startswith('apk-analysis/tsl9-') and not p.exists():
        p = root / ('analysis/' + name.removeprefix('apk-analysis/tsl9-'))
    return p


def module(p):
    s = importlib.util.spec_from_file_location('nv_write_source_' + p.parent.name + p.stem, p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def closed(folder, pin):
    need(sha(folder / 'seal.json') == pin, 'Pinned prior seal ' + str(folder))
    members = read(folder / 'seal.json')['members']
    rows = members.items() if isinstance(members, dict) else [(x['path'], x) for x in members]
    for name, value in rows:
        digest = value if isinstance(value, str) else value['sha256']
        need(sha(folder / name) == digest, 'Pinned prior member ' + name)


def context(root):
    folder = locate(root, 'analysis/v4160-callback-frontiers-2026-10-22/binding-review')
    closed(folder, BINDING)
    old = module(folder / 'check.py')
    C, decode, _, _ = old.context(root)
    return C, decode


def inspect(root, firmware=None):
    C, decode = context(root)
    record = read(HERE / 'original-contract.json')
    groups = record['groups']
    original = read(locate(root, 'analysis/v4160-callback-frontiers-2026-10-22/binding-review/ledger.json'))
    need(groups == {k: original['groups'][k] for k in groups}, 'Unchanged complete original source groups')
    rawfw = None
    if firmware is not None:
        rawfw = Path(firmware).read_bytes()
        need(hashlib.sha256(rawfw).hexdigest() == FW, 'Actual original firmware identity')
    for name, rows in groups.items():
        blob = b''.join(bytes.fromhex(x['raw_hex']) for x in rows)
        start = rows[0]['PC']
        need(C.rows(blob, start, decode) == rows, 'Complete raw original operands ' + name)
        if rawfw is not None:
            need(rawfw[start - 0x8000:start - 0x8000 + len(blob)] == blob, 'Actual firmware slice ' + name)
    need(sum(sum(x['bytes'] for x in rows) for rows in groups.values()) == 294
         and sum(len(rows) for rows in groups.values()) == 115, 'Source 294 B / 115 rows')
    t = {x['PC']: x for x in groups['timer']}
    w = {x['PC']: x for x in groups['write_cb']}
    p = {x['PC']: x for x in groups['program']}

    def exact(index, pc, **fields):
        need(all(index[pc][key] == value for key, value in fields.items()), 'Source operand ' + hex(pc))

    calls = [x['target'] for x in groups['write_cb'] if x['op'] == 'jal' and x['rd'] == 1]
    need(calls == [0x18e98, 0x18ec4, 0x18ef2, 0x18eb6, 0x19764], 'Five original real call targets/order')
    exact(w, 0x197be, op='addi', rd=2, rs1=2, immediate=-32)
    exact(w, 0x197c4, op='sw', rs1=2, rs2=12, immediate=12)
    exact(w, 0x197c6, op='mv', rd=8, rs1=10)
    exact(w, 0x197cc, op='mv', rd=10, rs1=8)
    exact(w, 0x197d2, op='lw', rd=12, rs1=2, immediate=12)
    exact(w, 0x197d4, op='mv', rd=10, rs1=8)
    exact(w, 0x197d6, op='mv', rd=11, rs1=12)
    exact(w, 0x197e0, op='addi', rd=10, rs1=0, immediate=1)
    exact(w, 0x197ea, op='addi', rd=10, rs1=0, immediate=0)
    need(not any(11 in (x['rs1'], x['rs2']) for x in groups['write_cb'] if x['PC'] < 0x197d6), 'Original entry A1 unused')
    exact(p, 0x18f16, op='addi', rd=12, rs1=0, immediate=256)
    need(not any(12 in (x['rs1'], x['rs2']) for x in groups['program'] if x['PC'] < 0x18f16), 'Program incoming A2 ignored before count definition')
    exact(t, 0x19764, op='lui', rd=15, immediate=0xe000f000)
    exact(t, 0x1976c, op='andi', rd=14, rs1=14, immediate=-2)
    exact(t, 0x19770, op='lbu', rd=14, rs1=3, immediate=382)
    exact(t, 0x19774, op='mul', rd=12, rs1=14, rs2=10)
    exact(t, 0x1977e, op='ori', rd=14, rs1=14, immediate=16)
    exact(t, 0x19786, op='ori', rd=14, rs1=14, immediate=33)
    exact(t, 0x1978e, op='andi', rd=14, rs1=14, immediate=1)
    exact(t, 0x19790, op='beq', rs1=14, rs2=0, target=0x1978c)
    exact(t, 0x19794, op='andi', rd=14, rs1=14, immediate=-2)
    accesses = [(x['PC'], x['op'], x['memory_width'], x['rs1'], x['immediate'])
                for x in groups['timer'] if x['memory_width']]
    expected = [(0x19768, 'lw', 32, 15, 4), (0x1976e, 'sw', 32, 15, 4),
                (0x19770, 'lbu', 8, 3, 382), (0x19778, 'sw', 32, 15, 16),
                (0x1977a, 'sw', 32, 15, 20), (0x1977c, 'lw', 32, 15, 0),
                (0x19782, 'sw', 32, 15, 0), (0x19784, 'lw', 32, 15, 0),
                (0x1978a, 'sw', 32, 15, 0), (0x1978c, 'lw', 32, 15, 4),
                (0x19792, 'lw', 32, 15, 0), (0x19796, 'sw', 32, 15, 0)]
    need(accesses == expected, 'Every original timer effect width/offset/order')
    need(not any(x['rd'] in (1, 2, 3, 4, 8, 9, 10, 11, *range(18, 28)) for x in groups['timer']), 'Original leaf timer preserves A0/A1 and structural bank')
    return dict(passed=True, original_bytes=294, original_rows=115, groups=6,
                actual_original_firmware_read=rawfw is not None, timer_minimum_effects=12,
                original_timer_A0_A1_preserved=True, write_frame_bytes=32,
                program_incoming_A2_ignored=True, full_original_ABI_proved=False,
                fault_or_IRQ_equivalence=False, target_execution=False)
