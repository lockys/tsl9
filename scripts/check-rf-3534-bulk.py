#!/usr/bin/env python3
"""Pin bounded RF call-site bytes; host-side interval model, not execution."""
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
base = runpy.run_path(str(ROOT / 'scripts/check-rf-3534-config.py'))
# Individual source instructions, in file byte order. Windows also pin guards,
# register definitions, and intervening instructions.
INSNS = {
    0x64bc0: 'aa84', 0x64bce: '37390020', 0x64bd2: '13060002',
    0x64bd6: '8145', 0x64bd8: '13050954', 0x64bdc: '97b0f91f',
    0x64be0: 'e780007c', 0x64be4: '13060002', 0x64be8: 'a685',
    0x64bea: '13050954', 0x64bee: '97b0f91f', 0x64bf2: 'e7804074',
    0x64d20: '2a8c', 0x64d32: 'ae84', 0x64d34: 'b28b',
    0x64e0e: '0850', 0x64e10: '63080c0c', 0x64e14: '23007501',
    0x64e18: '04b1', 0x64e1a: '2686', 0x64e1c: 'e285',
    0x64e1e: '0905', 0x64e20: '97b0f91f', 0x64e24: 'e7802051',
    0x64ee0: '23207501',
}

def verify_instructions(image):
    for pc, expected in INSNS.items():
        actual = image[pc - 0x40000:pc - 0x40000 + len(expected)//2]
        if actual.hex() != expected:
            raise ValueError(f'instruction mismatch {pc:#x}')
    return True

def overlaps(start, length, target=0x20003534):
    """Nonwrapping valid 32-bit address interval only; zero length writes nothing."""
    if not (0 <= start <= 0xffffffff and 0 <= length <= 0x100000000 - start):
        raise ValueError('invalid or wrapping range')
    return length > 0 and start < target + 4 and target < start + length

def verify(image, header):
    base['verify'](image, header)
    verify_instructions(image)
    return {'config_destination': '0x20003540', 'config_length': 32,
            'tx_copy_destination': 'then-loaded [0x20003534] + 2',
            'tx_copy_source': 'RF_Tx entry a0', 'tx_copy_length': 'RF_Tx entry a1',
            'config_clear_call_target': '0x2000039c', 'copy_call_target': '0x20000332',
            'helper_effects_unverified': True}

if __name__ == '__main__':
    print(json.dumps(verify(base['base']['IMAGE'].read_bytes(), base['base']['HEADER'].read_bytes()), indent=2))
