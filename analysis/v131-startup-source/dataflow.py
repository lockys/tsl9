#!/usr/bin/env python3
"""Bounded, offline V1.31 missing-word dataflow audit; not an execution model."""
import json
import runpy
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
source = runpy.run_path(str(HERE / 'check.py'))
dec = runpy.run_path(str(ROOT / 'analysis/resident-entry-reference-2026-10-21/source/inspect-source.py'))
BASE = 0x40000
# First copy maps flash 0x402b0 to RAM 0x20000040, if it completes.
SETTER = bytes.fromhex('b737002023aca7ee11c5b73700200547238ee7ee8280')
RUNNER = bytes.fromhex('b737002003a787ef411122c406c6138487ef11c30297b737002083c7c7ef93f7f70f99e323200400b240224441018280')

def audit(main):
    dec['gate'](main)
    def at(p, n): return main[p-BASE:p-BASE+n]
    def require(ok, msg):
        if not ok: raise ValueError(msg)
    require(at(0x409fa, len(SETTER)) == SETTER, 'setter instructions changed')
    require(at(0x40a10, len(RUNNER)) == RUNNER, 'runner instructions changed')
    require(dec['word'](main, 0x409fa) == 0x200037b7, 'setter base')
    require(dec['store'](main, 0x409fe) == (10, 15, -264, 2), 'setter pointer store')
    require(dec['word'](main, 0x40a10) == 0x200037b7, 'runner base')
    require(dec['load'](main, 0x40a14) == (14, 15, -264, 2), 'runner pointer load')
    require(at(0x40a22, 4) == bytes.fromhex('11c30297'), 'runner null guard or indirect call changed')
    require(dec['store'](main, 0x40a34) == (0, 8, 0, 2), 'runner conditional clear')
    return {'copy_last_source': '0x6eb2c', 'copy_last_destination': '0x20002ef8',
            'conditional_zero_first_store_source_pc': '0x402a8',
            'setter_store_ram_pc': '0x2000078e', 'runner_load_ram_pc': '0x200007a4',
            'runner_clear_ram_pc': '0x200007c4',
            'conditional_runner': {'load_source_pc': '0x40a14', 'load_ram_pc': '0x200007a4',
                'guard_source_pc': '0x40a22', 'guard_ram_pc': '0x200007b2',
                'jalr_source_pc': '0x40a24', 'jalr_ram_pc': '0x200007b4',
                'loaded_register': 'a4', 'jalr_target': 'a4 & ~1',
                'requires_observation_before_zero_and_runner_entry': True},
            'scope': 'selected instruction windows only',
            'other_readers_excluded': False, 'hardware_accessed': False, 'flashable': False}

def byte_witnesses():
    """Symbolic alternatives, not values for the absent source or a memory provider."""
    rows = []
    for i in range(4):
        # Two hypothetical words differing in only this byte. JALR clears bit 0.
        other = (2 if i == 0 else 1) << (8 * i)
        rows.append({'byte': i, 'zero_guard_differs': bool(other),
                     'jalr_target_differs': (other & ~1) != 0})
    return rows

def main():
    raw = (HERE / 'wchble_rom.hex').read_bytes()
    if source['digest'](raw) != source['HEX_SHA']: raise ValueError('HEX hash mismatch')
    mem = source['parse'](raw)
    main_bytes = bytes(mem[p] for p in range(0x40000, 0x6ea66))
    if source['digest'](main_bytes) != source['MAIN_SHA']: raise ValueError('main hash mismatch')
    if any(p in mem for p in range(0x6eb2c, 0x6eb30)): raise ValueError('missing source changed')
    result = audit(main_bytes)
    result['symbolic_single_byte_witnesses'] = byte_witnesses()
    print(json.dumps(result, indent=2))

if __name__ == '__main__': main()
