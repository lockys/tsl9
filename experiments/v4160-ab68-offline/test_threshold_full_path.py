#!/usr/bin/env python3
"""Compose post-getter threshold, state-bit branch and tail projections.

External call paths stop before the provider. Other paths use one synthetic
memory image through both reads and the tail. This is not a CPU or device test;
ordinary accesses succeed and no asynchronous side effects occur.
"""
import hashlib
import unittest

import caller_threshold_branch as threshold_branch
import caller_threshold_projection as prefix
import test_post_threshold_bit_branch as bit_branch
import test_tail_instruction_decoder as tail

MASK = 0xffffffff


class FullPathTests(unittest.TestCase):
    def test_threshold_to_call_or_tail(self):
        image = prefix.BIN.read_bytes()
        self.assertEqual(hashlib.sha256(image).hexdigest(), prefix.SHA)
        self.assertEqual(image[prefix.START-0x8000:prefix.START-0x8000+len(prefix.CODE)], prefix.CODE)
        threshold_branch.verify_image(image)
        self.assertEqual(image[bit_branch.START-0x8000:bit_branch.START-0x8000+len(bit_branch.CODE)], bit_branch.CODE)
        tails = {0x103da: image[0x103da-0x8000:0x103ea-0x8000],
                 0x103f8: image[0x103f8-0x8000:0x10402-0x8000]}
        counts = [0, 0, 0]
        for value in range(256):
            threshold = (5 * value + 10) & 255
            for state in (0, 1, 255):
                for s0 in (0, threshold, threshold + 1, 0xffffffff):
                    for byte in (0, 1, 2, 255):
                        for oldbit in (0, 1, 2):
                            sp = 0x2000
                            gp = (sp + 12 - 82) & MASK
                            slot, flag, source = (gp + 82) & MASK, (gp + 308) & MASK, sp + 32
                            memory = {(sp + i) & MASK: (i * 13 + 7) & 255 for i in range(16)}
                            memory.update({slot: oldbit, flag: state, source: byte})
                            before = memory.copy()
                            a0, a4, a5, events = prefix.run(prefix.CODE, value, gp, memory)
                            self.assertEqual((a0, a4, a5, events),
                                             (threshold, state, threshold, [('read', flag, state)]))
                            pc, call, projected, writes = threshold_branch.run(a5, a4, s0, gp)
                            should_call = (state == 0 and s0 > threshold > 59) or (state != 0 and s0 <= threshold)
                            if should_call:
                                expected = 1 if state == 0 else 0
                                self.assertEqual((pc, call, projected, writes),
                                                 (0x103c6, (0x167a6, 159 if state == 0 else 158),
                                                  {flag: expected}, [('write', flag, expected)]))
                                counts[0] += 1
                                continue
                            self.assertEqual((pc, call, projected, writes), (0x103ca, None, {flag: state}, []))
                            target, bit, reads = bit_branch.project(bit_branch.CODE, source - 7, gp, memory)
                            expected_bit = (byte >> 1) & 1
                            different = oldbit != expected_bit
                            self.assertEqual((target, bit, reads),
                                             (0x103da if different else 0x103f8, expected_bit,
                                              [('read', source, byte), ('read', slot, oldbit)]))
                            def word(offset):
                                return sum(before[(sp + offset + i) & MASK] << (8 * i) for i in range(4))
                            result = tail.execute(tails[target], target, sp, gp, bit, memory)
                            expected_events = [('read32', sp + off, word(off))
                                               for off in ((8, 12, 4) if different else (12, 8, 4))]
                            if different:
                                expected_events.append(('write8', slot, expected_bit))
                            self.assertEqual(result, (sp + 16, (word(8), word(12), word(4)),
                                                      0x13c4e if different else word(12) & ~1, expected_events))
                            if different:
                                before[slot] = expected_bit
                            self.assertEqual(memory, before)
                            counts[1 if different else 2] += 1
        self.assertTrue(all(counts), counts)
        self.assertEqual(sum(counts), 256 * 3 * 4 * 4 * 3)


if __name__ == '__main__':
    unittest.main()
