#!/usr/bin/env python3
"""Compose the original post-threshold branch and tail projections offline.

Successful ordinary RAM accesses only. The tail decoder recognizes compressed
instructions by exact encoding. This does not model asynchronous changes,
alignment faults, the callee, reachability, or physical hardware.
"""
import hashlib
import unittest

import caller_threshold_projection as firmware
import test_post_threshold_bit_branch as branch
import test_tail_instruction_decoder as tail

MASK = 0xffffffff


class PostThresholdComposition(unittest.TestCase):
    def test_original_branch_and_tails_with_stack_aliases(self):
        image = firmware.BIN.read_bytes()
        self.assertEqual(hashlib.sha256(image).hexdigest(), firmware.SHA)
        code = image[branch.START - 0x8000:branch.START - 0x8000 + len(branch.CODE)]
        self.assertEqual(code, branch.CODE)
        changed = image[0x103da - 0x8000:0x103ea - 0x8000]
        unchanged = image[0x103f8 - 0x8000:0x10402 - 0x8000]
        counts = [0, 0]
        for value in range(256):
            for state in range(256):
                # The state byte may overlap any byte in the three saved words.
                sp = 0xfffffff8 if (value & 1) else 0x1000
                slot = (sp + (4, 8, 12)[state % 3] + (value % 4)) & MASK
                gp = (slot - 82) & MASK
                source = (sp + 24) & MASK
                s1 = (source - 7) & MASK
                memory = {(sp + i) & MASK: (i * 17 + state) & 255 for i in range(32)}
                memory[source] = value
                memory[slot] = state
                before = memory.copy()
                target, bit, reads = branch.project(code, s1, gp, memory)
                expected_bit = (value >> 1) & 1
                different = state != expected_bit
                self.assertEqual((target, bit, reads),
                                 (0x103da if different else 0x103f8, expected_bit,
                                  [('read', source, value), ('read', slot, state)]))
                def word(offset):
                    return sum(before[(sp + offset + i) & MASK] << (8 * i) for i in range(4))
                actual = tail.execute(changed if different else unchanged, target, sp, gp, bit, memory)
                ordered = (8, 12, 4) if different else (12, 8, 4)
                events = [('read32', (sp + off) & MASK, word(off)) for off in ordered]
                if different:
                    events.append(('write8', slot, expected_bit))
                expected_target = 0x13c4e if different else word(12) & ~1
                self.assertEqual(actual, ((sp + 16) & MASK, (word(8), word(12), word(4)),
                                          expected_target, events))
                expected_memory = before.copy()
                if different:
                    expected_memory[slot] = expected_bit
                self.assertEqual(memory, expected_memory)
                counts[int(different)] += 1
        self.assertEqual(counts, [256, 65280])


if __name__ == '__main__':
    unittest.main()
