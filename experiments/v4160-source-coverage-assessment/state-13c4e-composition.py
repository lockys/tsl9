#!/usr/bin/env python3
"""Compose the bounded 13c4e gate, post-call difference and two tail models.

The 81b0 provider is injected, not emulated. Assume it returns normally,
preserves gp/sp and the saved return slot, and no asynchronous interference
occurs. The gp+340 word must not overlap the saved return slot. Its return
and post-call gp+340 word are independently supplied.
Memory accesses succeed. The unrestricted return is an overapproximation:
conditional on normal 0x81b0 wrapper execution its actual output is at most
0x0fffffff. This does not prove actual provider behavior, target execution,
scheduler effects, runtime reachability, or a flashable image.
"""
import argparse
import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gate = load('state_gate', 'state-13c4e-gate.py')
delta = load('state_delta', 'state-13ca2-delta.py')
tail = load('state_tail', 'state-13cb4-tail.py')
CALL_PC = 0x13c9e
CALL_BYTES = bytes.fromhex('411106c6ef402fd1')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def prepare(image):
    need(hashlib.sha256(image).hexdigest() == gate.SHA256, 'firmware SHA-256')
    def window(start, end):
        return image[start-gate.BASE:end-gate.BASE]
    gate_code = window(gate.START, gate.STOP)
    call_code = window(0x13c9a, 0x13ca2)
    delta_code = window(delta.PC, delta.END)
    tail_code = window(tail.START, tail.STOP)
    need(gate_code == gate.CODE and call_code == CALL_BYTES and delta_code == delta.CODE,
         'gate, call or delta identity')
    need(tail_code == tail.CODE, 'tail identity')
    call = int.from_bytes(call_code[4:8], 'little')
    # The normal-call JAL must write ra (x1); reuse JAL target decoding after
    # clearing rd, which the helper otherwise requires to be x0.
    need((call & 0xfff) == 0xef, 'provider call is not jal ra')
    need(tail.jal_target(CALL_PC, call & ~(31 << 7)) == 0x81b0, 'provider call target')
    return gate_code, delta_code, tail_code


def compose(codes, first, second, gp, caller_sp, saved_ra, provider):
    gate_code, delta_code, tail_code = codes
    next_pc, reads = gate.machine(gate_code, gate.fixture(first, second))
    if next_pc == 0x13cda:
        return reads, [], None, 0x13cda, (), caller_sp, saved_ra
    need(next_pc == 0x13c9a, 'unexpected gate exit')
    word_bytes = {((gp + 340 + i) & tail.MASK) for i in range(4)}
    saved_bytes = {((caller_sp - 4 + i) & tail.MASK) for i in range(4)}
    need(word_bytes.isdisjoint(saved_bytes), 'saved return slot overlaps post-call word')
    current, stored_after = provider()
    address, difference, next_pc = delta.project(delta_code, gp, current, stored_after)
    ra, new_sp, write, target, args = tail.project(
        tail_code, next_pc == delta.END, gp, (caller_sp-16) & tail.MASK, current, saved_ra)
    need(address == (gp+340) & tail.MASK, 'post-call load address')
    return reads, [0x81b0], write, target, args, new_sp, ra


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bin', type=Path)
    args = parser.parse_args()
    codes = prepare(args.bin.read_bytes())
    records = ((0xfffe, 1, 1), (0xffff, 1, 1), (0, 1, 0), (0, 0, 1))
    cases = 0
    for first in records:
        for second in records:
            expected_gate, expected_reads = gate.oracle(first, second)
            for previous in (0, 1, 0xfffffff0, 0xffffffff):
                for difference in (0, 1, 33, 34, 35, 36, 0x7fffffff, 0xffffffff):
                    for overwrite in (False, True):
                        # Provider may change gp+340; stale previous value is not
                        # assumed to be the word loaded after the call.
                        after = (previous+1) & tail.MASK if overwrite else previous
                        current = (after+difference) & tail.MASK
                        calls = []
                        def provider():
                            calls.append(True)
                            return current, after
                        got = compose(codes, first, second, 0x20004000, 0x2000ff00, 0x12345678, provider)
                        qualifies = expected_gate == 0x13c9a
                        direct = difference > 34
                        expected = (expected_reads, [0x81b0] if qualifies else [],
                                    (0x20004154, current) if qualifies and direct else None,
                                    (0x137c0 if direct else 0x9124) if qualifies else 0x13cda,
                                    ((0,) if direct else (0x137c0, 0, 35, 0)) if qualifies else (),
                                    0x2000ff00, 0x12345678)
                        need(got == expected and len(calls) == int(qualifies), 'composition mismatch')
                        cases += 1
    print(f'PASS: {cases} bounded compositions; supplied provider return and post-call word varied')
    print('LIMIT: provider modeled, not executed; no target, scheduler, interrupts, faults or reachability')


if __name__ == '__main__':
    main()
