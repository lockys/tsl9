#!/usr/bin/env python3
"""Compose the 13c4e gate, wrapper and tail using one synthetic data memory.

All eight gate-record bytes must be initialized, even if the gate short-circuits.
The gate reads them before any call-frame store; the returned tail store is
applied only after the modeled saved-ra load. The component models retain their
own restrictions, including gp+340 not overlapping the outer saved-ra word.
Assumes successful accesses and normal returns with gp/sp and outer saved-ra
preserved. Injected resident, no interrupts/faults/instruction mutation, no
hardware, execution-reachability or downstream-scheduler proof.
"""
import argparse
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('composition', Path(__file__).with_name('state_13c4e_wrapper_composition.py'))
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
w, state = c.wrapper, c.state


def records(memory):
    base = state.gate.DATA
    try:
        values = [memory[(base+i) & w.MASK] for i in range(2, 10)]
    except KeyError as exc:
        raise ValueError('uninitialized gate fixture byte') from exc
    state.need(all(isinstance(x, int) and 0 <= x <= 255 for x in values), 'invalid gate byte')
    def record(offset):
        return (values[offset] | values[offset+1] << 8, values[offset+3], values[offset+2])
    return record(0), record(4)


def check_memory(memory):
    state.need(all(isinstance(k, int) and 0 <= k <= w.MASK and
                   isinstance(v, int) and 0 <= v <= 255 for k, v in memory.items()),
               'invalid synthetic byte memory')


def run(codes, wrapper_code, memory, gp, sp, saved_ra, resident):
    check_memory(memory)
    first, second = records(memory)
    expected_pc, expected_reads = state.gate.machine(codes[0], memory)
    def checked_resident(target, frame, mem):
        result = resident(target, frame, mem)
        check_memory(mem)
        return result
    result = c.run(codes, wrapper_code, first, second, gp, sp, saved_ra, memory, checked_resident)
    state.need(result[0] == expected_reads, 'gate read trace mismatch')
    state.need((result[3] == 0x13cda) == (expected_pc == 0x13cda), 'gate decision mismatch')
    if result[2] is not None:
        w.store32(memory, *result[2])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bin', type=Path)
    args = parser.parse_args()
    codes, code = c.prepare(args.bin.read_bytes())
    choices = ((0xfffe, 1, 1), (0xffff, 1, 1), (0, 1, 0), (0, 0, 1))
    cases = 0
    for first in choices:
        for second in choices:
            for raw in (0, 55, 56, 0x19999999, 0xffffffff):
                for initial in (0, 34, 0xffffffff):
                    memory = state.gate.fixture(first, second)
                    w.store32(memory, w.SLOT, 0x12345679)
                    w.store32(memory, 0x20004154, initial)
                    calls = []
                    def resident(target, frame, mem):
                        state.need(target == 0x12345678, 'resident target')
                        calls.append(target)
                        return raw, frame
                    expected_pc, reads = state.gate.oracle(first, second)
                    result = run(codes, code, memory, 0x20004000, 0x2000ff00, 0x12345678, resident)
                    state.need(result[0] == reads and len(calls) == int(expected_pc == 0x13c9a), 'gate/call')
                    if expected_pc == 0x13c9a:
                        scaled = ((raw*10) & w.MASK) >> 4
                        direct = ((scaled-initial) & w.MASK) > 34
                        state.need(result[3] == (0x137c0 if direct else 0x9124), 'tail target')
                        state.need(w.load32(memory, 0x20004154) == (scaled if direct else initial), 'tail store')
                    else:
                        state.need(result[3] == 0x13cda, 'gate exit')
                    cases += 1
    print(f'PASS: {cases} single-data-memory compositions with gate and applied tail store')
    print('LIMIT: synthetic resident, mapped data and normal returns; no device execution')


if __name__ == '__main__':
    main()
