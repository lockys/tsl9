#!/usr/bin/env python3
"""Bounded syntactic forward scan, not disassembly, reachability or execution.

Each halfword in the supplied marked code ranges is an independent possible
start. Unsupported encodings kill all facts and terminate that candidate block.
"""
import argparse
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECT = runpy.run_path(str(ROOT / 'scripts/scan-rf-pointer-direct.py'))
TARGET = 0x20003538
MASK = 0xffffffff


def sx(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def scan(data, base, ranges, budget=32):
    if budget < 1:
        raise ValueError('budget must be positive')
    hits, stops = {}, {}
    counts = {'origins': 0, 'instructions_examined': 0, 'unknown_stop_paths': 0, 'range_end_paths': 0, 'budget_stop_paths': 0}
    for start, end in ranges:
        if start % 2 or end % 2 or not base <= start < end <= base + len(data):
            raise ValueError('invalid marked code range')
        for origin in range(start, end, 2):
            counts['origins'] += 1
            regs = [None] * 32
            regs[0] = 0
            pc = origin
            for _ in range(budget):
                i = pc - base
                if pc + 2 > end:
                    counts['range_end_paths'] += 1
                    break
                counts['instructions_examined'] += 1
                h = int.from_bytes(data[i:i + 2], 'little')
                size = 2 if h & 3 != 3 else 4
                if pc + size > end or (size == 4 and h & 0x1f == 0x1f):
                    stops[pc] = 'truncated or unsupported length'
                    counts['unknown_stop_paths'] += 1
                    break
                w = int.from_bytes(data[i:i + size], 'little')
                rd = (w >> 7) & 31
                rs1 = (w >> 15) & 31
                op = w & 127
                recognized = False
                store = None
                if size == 4:
                    if op == 0x37:  # LUI
                        if rd: regs[rd] = w & 0xfffff000
                        recognized = True
                    elif op == 0x17:  # AUIPC
                        if rd: regs[rd] = (pc + (w & 0xfffff000)) & MASK
                        recognized = True
                    elif op == 0x13 and (w >> 12 & 7) == 0:  # ADDI, including MV
                        if rd: regs[rd] = None if regs[rs1] is None else (regs[rs1] + sx(w >> 20, 12)) & MASK
                        recognized = True
                    elif op == 0x33 and (w >> 12 & 7) == 0 and w >> 25 == 0:  # ADD
                        rs2 = w >> 20 & 31
                        if rd: regs[rd] = None if regs[rs1] is None or regs[rs2] is None else (regs[rs1] + regs[rs2]) & MASK
                        recognized = True
                    elif op == 0x23 and (w >> 12 & 7) in (0, 1, 2):
                        imm = sx((w >> 25) << 5 | (w >> 7 & 31), 12)
                        store = (rs1, imm, 1 << (w >> 12 & 7), w >> 20 & 31)
                        recognized = True
                    elif op == 3 and (w >> 12 & 7) in (0, 1, 2, 4, 5):
                        if rd: regs[rd] = None
                        recognized = True
                else:
                    q, f = h & 3, h >> 13
                    if q == 1 and f == 0:  # C.ADDI / NOP
                        imm = sx(((h >> 12 & 1) << 5) | (h >> 2 & 31), 6)
                        if rd: regs[rd] = None if regs[rd] is None else (regs[rd] + imm) & MASK
                        recognized = True
                    elif q == 1 and f == 2 and rd:  # C.LI
                        regs[rd] = sx(((h >> 12 & 1) << 5) | (h >> 2 & 31), 6) & MASK
                        recognized = True
                    elif q == 2 and f == 4 and not (h >> 12 & 1) and rd and (h >> 2 & 31):  # C.MV
                        regs[rd] = regs[h >> 2 & 31]
                        recognized = True
                    elif q == 0 and f == 6:  # C.SW
                        off = ((h >> 10 & 7) << 3) | ((h >> 6 & 1) << 2) | ((h >> 5 & 1) << 6)
                        store = (8 + (h >> 7 & 7), off, 4, 8 + (h >> 2 & 7))
                        recognized = True
                    elif q == 0 and f == 2:  # C.LW
                        regs[8 + (h >> 2 & 7)] = None
                        recognized = True
                if not recognized:
                    # Unknown may write any register or change control flow.
                    regs = [None] * 32
                    stops[pc] = 'unsupported/control flow: all facts killed'
                    counts['unknown_stop_paths'] += 1
                    break
                if store:
                    reg, off, width, source = store
                    if regs[reg] is not None:
                        address = (regs[reg] + off) & MASK
                        if any((address + k) & MASK in range(TARGET, TARGET + 4) for k in range(width)):
                            key = (origin, pc, address, width, source)
                            hits[key] = {'start': hex(origin), 'store_pc': hex(pc), 'address': hex(address), 'width': width, 'source_register': source, 'source_value': None if regs[source] is None else hex(regs[source]), 'base_value': hex(regs[reg]), 'offset': off, 'bytes': data[origin-base:pc-base+size].hex()}
                pc += size
            else:
                counts['budget_stop_paths'] += 1
    return {'counts': counts, 'hits': list(hits.values()), 'unsupported_or_control_stops': len(stops), 'stop_examples': [hex(x) for x in sorted(stops)[:20]]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--range', action='append', required=True, metavar='START:END', help='explicit marked code range, end exclusive')
    parser.add_argument('--budget', type=int, default=32)
    args = parser.parse_args()
    ranges = [tuple(int(v, 0) for v in s.split(':')) for s in args.range]
    data = DIRECT['IMAGE'].read_bytes()
    DIRECT['verify'](data)  # pinned contiguous sparse-carrier segment, no gap filling
    result = scan(data, DIRECT['BASE'], ranges, args.budget)
    print(json.dumps({'sha256': DIRECT['SHA'], 'ranges': args.range, 'budget': args.budget, 'exhaustive': False, 'hardware_executed': False, **result}, indent=2))


if __name__ == '__main__':
    main()
