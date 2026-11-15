#!/usr/bin/env python3
"""Compose the bounded post-getter and branch projections, not a CPU run.

The same stable synthetic byte is used for the load and initial branch state.
Execution stops before the external call or unrelated continuation; effects of
asynchronous changes, callbacks, device memory and the getter are not modeled.
"""
import hashlib
import unittest
from unittest.mock import patch

import caller_threshold_branch as branch
import caller_threshold_projection as prefix


def compose(value, state, s0, gp):
    address = (gp + 308) & prefix.MASK
    a0, a4, a5, reads = prefix.run(prefix.CODE, value, gp, {address: state})
    if a0 != a5:
        raise ValueError('threshold registers differ')
    pc, call, memory, writes = branch.run(a5, a4, s0, gp)
    return pc, call, memory[address], reads + writes


def oracle(value, state, s0, gp):
    threshold = ((value & 0xffffffff) * 5 + 10) & 255
    address = (gp + 308) & 0xffffffff
    events = [('read', address, state)]
    if state == 0 and (s0 & 0xffffffff) > threshold > 59:
        events.append(('write', address, 1))
        return 0x103c6, (0x167a6, 159), 1, events
    if state != 0 and (s0 & 0xffffffff) <= threshold:
        events.append(('write', address, 0))
        return 0x103c6, (0x167a6, 158), 0, events
    return 0x103ca, None, state, events


class ThresholdCompositionTests(unittest.TestCase):
    def test_original_image_identity(self):
        image = prefix.BIN.read_bytes()
        self.assertEqual(hashlib.sha256(image).hexdigest(), prefix.SHA)
        self.assertEqual(image[prefix.START-0x8000:prefix.START-0x8000+len(prefix.CODE)], prefix.CODE)
        branch.verify_image(image)

    def test_all_bytes_and_boundary_registers(self):
        cases = 0
        for value in range(256):
            for state in range(256):
                threshold = (5 * value + 10) & 255
                s0 = (threshold - 1, threshold, threshold + 1, 0xffffffff)[state & 3] & 0xffffffff
                gp = (0x20004000, 0xfffffecc)[state & 1]
                self.assertEqual(compose(value, state, s0, gp), oracle(value, state, s0, gp))
                cases += 1
        self.assertEqual(cases, 65536)

    def test_each_boundary_for_all_return_bytes_and_states(self):
        cases = 0
        for value in range(256):
            threshold = (5 * value + 10) & 255
            for state in (0, 1, 255):
                for s0 in (0, (threshold - 1) & 0xffffffff, threshold,
                           threshold + 1, 0xffffffff):
                    for gp in (0x20004000, 0xfffffecc):
                        self.assertEqual(compose(value, state, s0, gp),
                                         oracle(value, state, s0, gp))
                        cases += 1
        self.assertEqual(cases, 7680)

    def test_full_width_getter_returns(self):
        for value in (0x100, 0x101, 0x10000, 0x80000000, 0xffffffff):
            for state in (0, 1, 255):
                for s0 in (0, 60, 255, 0xffffffff):
                    with self.subTest(value=value, state=state, s0=s0):
                        self.assertEqual(compose(value, state, s0, 0x20004000),
                                         oracle(value, state, s0, 0x20004000))

    def test_branch_condition_mutation_is_observable(self):
        original = branch.SEGMENTS[0x103ae]
        # Change the first BLTU at 0x103b0 into BGEU without changing operands.
        changed = bytearray(original)
        changed[3] ^= 0x10
        mutated = dict(branch.SEGMENTS)
        mutated[0x103ae] = bytes(changed)
        with patch.object(branch, 'SEGMENTS', mutated):
            self.assertNotEqual(compose(10, 0, 100, 0x20004000),
                                oracle(10, 0, 100, 0x20004000))


if __name__ == '__main__':
    unittest.main()
