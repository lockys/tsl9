#!/usr/bin/env python3
"""Connect 13c4e projection to 81b0 projection with shared data memory.

The gate fixture is independent of memory passed here; the returned tail write
is not applied to that memory. Assumptions: successful memory accesses; no
instruction mutation or asynchronous interference; gp preserved; both calls
return normally; wrapper returns to 13ca2 with the stack pointer and the outer
saved return word unchanged. The resident body is an injected callback. No proof
of target reachability, resident, scheduler or hardware behavior is made.
"""
import argparse
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


state = load('state_composition', 'state-13c4e-composition.py')
wrapper = load('wrapper', 'wrapper-81b0.py')


def prepare(image):
    codes = state.prepare(image)
    code = image[wrapper.START-wrapper.BASE:wrapper.END-wrapper.BASE]
    wrapper.validate(code)
    return codes, code


def run(codes, code, first, second, gp, sp, saved_ra, memory, resident):
    outer_slot = (sp-4) & wrapper.MASK
    def provider():
        wrapper.store32(memory, outer_slot, saved_ra)
        value, live_sp, live_ra, target = wrapper.project(
            code, memory, (sp-16) & wrapper.MASK, 0x13ca2, resident)
        state.need(live_sp == (sp-16) & wrapper.MASK, 'wrapper stack changed')
        state.need(target == 0x13ca2, 'wrapper return changed')
        state.need(wrapper.load32(memory, outer_slot) == saved_ra & wrapper.MASK,
                   'outer saved return changed')
        return value, wrapper.load32(memory, (gp+340) & wrapper.MASK)
    return state.compose(codes, first, second, gp, sp, saved_ra, provider)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bin', type=Path)
    args = parser.parse_args()
    codes, code = prepare(args.bin.read_bytes())
    first, second = (0xffff, 1, 1), (0xfffe, 0, 0)
    cases = 0
    for raw in (0, 1, 2, 54, 55, 56, 0x19999999, 0x1999999a, 0x7fffffff, 0xffffffff):
        for initial in (0, 1, 34, 35, 0xffffffff):
            for updated in (False, True):
                memory = {}
                wrapper.store32(memory, wrapper.SLOT, 0x12345679)
                wrapper.store32(memory, 0x20004154, initial)
                after = (initial+1) & wrapper.MASK if updated else initial
                def resident(target, frame, bus):
                    state.need(target == 0x12345678, 'indirect target')
                    if updated:
                        wrapper.store32(bus, 0x20004154, after)
                    return raw, frame
                result = run(codes, code, first, second, 0x20004000, 0x2000ff00,
                             0x12345678, memory, resident)
                scaled = ((raw*10) & wrapper.MASK) >> 4
                difference = (scaled-after) & wrapper.MASK
                target = 0x137c0 if difference > 34 else 0x9124
                write = (0x20004154, scaled) if difference > 34 else None
                _, reads = state.gate.oracle(first, second)
                args_out = (0,) if difference > 34 else (0x137c0, 0, 35, 0)
                expected = (reads, [0x81b0], write, target, args_out, 0x2000ff00, 0x12345678)
                state.need(result == expected, 'composition result')
                cases += 1
    print(f'PASS: {cases} state/wrapper/resident-injection compositions')
    print('LIMIT: modeled resident and stable return assumptions; no target or device execution')


if __name__ == '__main__':
    main()
