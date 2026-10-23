#!/usr/bin/env python3
"""Read-only raw instruction/CFG inventory, not ISA execution or reachability proof."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
FW = 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
FW_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
R2_SHA = 'cf307a66636960527e1511d00d2be6484b3b45929bf49f3d0923b24b13e17e58'
BEGIN, END = 0x14D2E, 0x154A6


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True)+'\n').encode()


def collect(r2):
    firmware = (ROOT/FW).read_bytes()
    need(digest(firmware) == FW_SHA and digest(r2.read_bytes()) == R2_SHA, 'Pinned original and existing reader')
    argv = [str(r2), '-N', '-q', '-a', 'riscv', '-b', '32', '-m', '0x8000', '-c',
            'e scr.color=0;pDj 1912 @ 0x14d2e;q', str(ROOT/FW)]
    process = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    need(process.returncode == 0, 'Read-only disassembly exited successfully')
    rows = json.loads(process.stdout)
    need(len(rows) == 666, 'Exactly666 instruction records')
    at = BEGIN
    for row in rows:
        size = row['size']
        need(row['addr'] == at and size in (2, 4) and row['opcode'] != 'invalid', 'Contiguous standard-width instructions')
        need(bytes.fromhex(row['bytes']) == firmware[at-0x8000:at-0x8000+size], 'Every reader byte is original')
        at += size
    need(at == END, 'Exact1912B candidate extent')
    starts = {r['addr'] for r in rows}
    tables = []
    for base, count, pc, expression in [(0x1A6B8, 7, 0x14D50, 'A0 from829E; unsigned guard A0<=6; index=A0'),
                                        (0x1A6D4, 8, 0x15362, '(byte[then-live S0+5]>>2)&7')]:
        raw = firmware[base-0x8000:base-0x8000+4*count]
        offsets = list(struct.unpack('<'+'i'*count, raw))
        targets = [(base+n) & 0xFFFFFFFF for n in offsets]
        need(all(t in starts for t in targets), 'Every table target is an original instruction start')
        tables.append(dict(base=base, bytes=len(raw), SHA256=digest(raw), JR_PC=pc,
                           signed_relative_offsets=offsets, targets=targets, index_expression=expression,
                           JR_writes_RA=False))
    computed = {t['JR_PC']: t['targets'] for t in tables}
    calls, tails, returns, edges = [], [], [], []
    for row in rows:
        pc, size, kind = row['addr'], row['size'], row['type']
        after = pc+size
        if pc in computed:
            need(row['opcode'] == 'jr a5', 'Known computed JR register')
            edges += [(pc, target) for target in computed[pc]]
        elif kind == 'call':
            need('jump' in row, 'Every direct call destination known')
            calls.append(dict(PC=pc, target=row['jump'], link_RA=after))
            need(after in starts, 'Normal-return call continuation stays in body')
            edges.append((pc, after))
        elif kind == 'cjmp':
            need(row['jump'] in starts and after in starts, 'Both conditional edges internal')
            edges += [(pc, row['jump']), (pc, after)]
        elif kind == 'jmp':
            target = row['jump']
            if target in starts:
                edges.append((pc, target))
            else:
                tails.append(dict(PC=pc, target=target, link_RA=False))
        elif kind == 'ret':
            returns.append(pc)
        else:
            need(kind not in ('rjmp', 'ucall', 'ujmp'), 'No guessed indirect frontier')
            need(after in starts, 'Ordinary fallthrough remains internal')
            edges.append((pc, after))
    need(len(calls) == 21 and len(tails) == 59 and returns == [0x14DA8], 'Complete direct/return inventory')
    adjacency = {}
    for origin, target in edges:
        adjacency.setdefault(origin, set()).add(target)
    reached, pending = set(), [BEGIN]
    while pending:
        pc = pending.pop()
        if pc in reached:
            continue
        reached.add(pc)
        pending += [x for x in adjacency.get(pc, ()) if x not in reached]
    need(reached == starts, 'All instruction starts covered by syntactic normal-return overapproximation')
    row_positions = {r['addr']: i for i, r in enumerate(rows)}
    for tail in tails:
        pos = row_positions[tail['PC']]
        before = rows[max(0, pos-10):pos]
        texts = [r['opcode'] for r in before]
        s0 = len(texts)-1-texts[::-1].index('lw s0, 8(sp)')
        ra = len(texts)-1-texts[::-1].index('lw ra, 12(sp)')
        sp = len(texts)-1-texts[::-1].index('addi sp, sp, 16')
        need(s0 < ra < sp, 'Every direct tail restores S0 then RA then SP')
        tail['restore_PCs'] = [before[n]['addr'] for n in (s0, ra, sp)]
    pos = row_positions[returns[0]]
    need([r['opcode'] for r in rows[pos-3:pos]] == ['lw ra, 12(sp)', 'lw s0, 8(sp)', 'addi sp, sp, 16'], 'Distinct RA-first common return')
    all_external = sorted({r['target'] for r in calls+tails})
    need(len(all_external) == 71, '71 distinct direct external targets')
    report = dict(schema='TSL9-feature-dispatch-frontier-v1', firmware=FW, firmware_SHA256=FW_SHA,
                  reader_SHA256=R2_SHA, producer='scripts/analyze-feature-dispatch.py',
                  producer_SHA256=digest(Path(__file__).read_bytes()),
                  span=[BEGIN, END], bytes=END-BEGIN, instructions=len(rows),
                  original_code_SHA256=digest(firmware[BEGIN-0x8000:END-0x8000]),
                  tables=tables, direct_calls=calls, distinct_callees=sorted({r['target'] for r in calls}),
                  direct_tails=tails, distinct_external_targets=all_external, common_return_PCs=returns,
                  internal_edges_with_table_entries=len(edges), unique_internal_edges=len(set(edges)),
                  covered_instruction_starts=len(reached),
                  CFG_semantics='Syntactic overapproximation assumes normal call returns and both branch outcomes; no runtime reachability proof.',
                  first_RET_is_not_function_end=True, following_154A6_is_separate_entry=True,
                  original_callee_ABI_assumed=False, complete_C_reconstruction=False,
                  target_executed=False, ISA_emulated=False, network=False, firmware_ready=False)
    return report, process.stdout, process.stderr, argv


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--r2', type=Path, default=Path.home()/'Tools/radare2/bin/r2.exe')
    actions = p.add_mutually_exclusive_group(required=True)
    actions.add_argument('--output', type=Path)
    actions.add_argument('--emit', action='store_true')
    actions.add_argument('--replay', type=Path)
    a = p.parse_args()
    report, raw, errors, argv = collect(a.r2.resolve())
    if a.emit:
        print(json.dumps(report, ensure_ascii=True))
        return
    if a.output:
        folder = a.output.resolve()
        need(folder.is_relative_to(ROOT/'build') and not folder.exists(), 'Create-only local build output')
        folder.mkdir(parents=True)
        (folder/'reader-output.json').write_bytes(raw)
        (folder/'reader-errors.log').write_bytes(errors)
        (folder/'actual-command.json').write_bytes(encoded(dict(argv=argv, exit=0)))
        (folder/'summary.json').write_bytes(encoded(report))
    else:
        need(json.loads(a.replay.read_bytes()) == report, 'Exact current dispatch report replay')
    print(json.dumps(dict(passed=True, bytes=report['bytes'], instructions=report['instructions'],
                          direct_call_sites=len(report['direct_calls']), direct_tail_sites=len(report['direct_tails']),
                          distinct_external_targets=len(report['distinct_external_targets']),
                          CFG_is_syntactic_overapproximation=True, firmware_ready=False)))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        print('FAIL: '+str(error), file=sys.stderr)
        sys.exit(1)
