"""Offline fixed-V1.31 startup instruction and sparse-HEX check; no target execution."""
import hashlib
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HEX = ROOT / 'analysis/wch-resident-candidate-2026-10-21/original-dec2023/wchble_rom.hex'
CARRIER = ROOT / 'analysis/resident-entry-reference-2026-10-21/reference-carrier/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin'
HEX_SHA = '11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5'
CARRIER_SHA = '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'

def require(condition, message):
    if not condition:
        raise ValueError(message)

def identity(data, expected):
    require(hashlib.sha256(data).hexdigest() == expected, 'fixed input hash mismatch')

def check():
    raw = HEX.read_bytes()
    carrier = CARRIER.read_bytes()
    identity(raw, HEX_SHA)
    identity(carrier, CARRIER_SHA)
    sparse_path = ROOT / 'experiments/tsl9-resident-initial-data-prefix/audit-v1.py'
    gate_path = ROOT / 'analysis/resident-entry-reference-2026-10-21/source/inspect-source.py'
    identity(sparse_path.read_bytes(), '15b7f1a864f1781a274e7c3a934ef4951272bc5af0d3f0a84b6553304dfc883d')
    identity(gate_path.read_bytes(), 'c78bb6a6825ee504701b74b5397992fbb7ab44e686d447751b6cc961ec3701b5')
    sparse = runpy.run_path(str(sparse_path))['sparse_hex']
    memory, inventory = sparse(HEX)
    require(len(carrier) == 191078 and all(memory.get(0x40000 + i) == b for i, b in enumerate(carrier)), 'carrier/HEX mismatch')
    gate = runpy.run_path(str(gate_path))['gate']
    values = gate(carrier)
    first, second = values['first'], values['second']
    require(first == [0x402b0, 0x20000040, 0x20002e70] and second == [0x6eaa4, 0x20002e70, 0x20002ef8], 'copy arguments')
    words = [(end - dst) // 4 + 1 for src, dst, end in (first, second)]
    require(words == [2957, 35], 'inclusive word counts')
    missing = [p for p in range(second[0], second[0] + words[1]*4) if p not in memory]
    require(missing == list(range(0x6eb2c, 0x6eb30)), 'missing word coverage')
    # Exercise raw instruction decoder separately from fixed hash admission.
    cases = [('first call target', 0x6de4e, 0x10), ('second call target', 0x6de6e, 0x10),
             ('inclusive guard', 0x40280, 0x10), ('source load', 0x40286, 0x20),
             ('destination store', 0x4028c, 0x20), ('zero tail', 0x6de7a, 0x10)]
    for label, pc, mask in cases:
        altered = bytearray(carrier)
        altered[pc - 0x40000] ^= mask
        try:
            gate(altered)
        except (ValueError, AssertionError):
            continue
        raise ValueError('mutation accepted: ' + label)
    for data, pin in ((raw, HEX_SHA), (carrier, CARRIER_SHA)):
        altered = bytearray(data)
        altered[20] ^= 1
        try:
            identity(altered, pin)
        except ValueError:
            continue
        raise ValueError('altered fixed input accepted')
    # A strict sparse provider refuses the actual final load, before any store/return/zero.
    def read32(address):
        require(all(address+i in memory for i in range(4)), 'uncaptured READ32')
        return bytes(memory[address+i] for i in range(4))
    require(len(read32(0x6eb28)) == 4, 'last captured word')
    try:
        read32(0x6eb2c)
    except ValueError:
        pass
    else:
        raise ValueError('missing READ32 accepted')
    print(json.dumps({'passed': True, 'hex_sha256': HEX_SHA, 'carrier_sha256': CARRIER_SHA,
        'records': inventory['records'], 'copy_words': words, 'missing': ['0x6eb2c', '0x6eb30'],
        'instruction_mutations_rejected': len(cases), 'hash_mutations_rejected': 2,
        'strict_missing_read_rejected': True, 'target_executed': False}, indent=2))

if __name__ == '__main__':
    check()
