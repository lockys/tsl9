#!/usr/bin/env python3
"""Additional shared-RAM alias cases for the post-threshold composition.

Synthetic successful accesses only; no alignment faults, interrupts, callee,
reachability or hardware claims. Original bytes are read and never modified.
"""
import hashlib
import unittest
from unittest.mock import patch

import caller_threshold_projection as firmware
import test_post_threshold_bit_branch as branch
import test_tail_instruction_decoder as tail

MASK = 0xffffffff


class AliasCompositionTests(unittest.TestCase):
    def test_input_state_and_saved_word_share_one_byte(self):
        image = firmware.BIN.read_bytes()
        self.assertEqual(hashlib.sha256(image).hexdigest(), firmware.SHA)
        self.assertEqual(image[branch.START - 0x8000:branch.START - 0x8000 + len(branch.CODE)], branch.CODE)
        changed = image[0x103da - 0x8000:0x103ea - 0x8000]
        unchanged = image[0x103f8 - 0x8000:0x10402 - 0x8000]
        destinations = {0x103da: changed, 0x103f8: unchanged}
        counts = [0, 0]
        for value in range(256):
            for saved_offset in (4, 8, 12):
                for byte_index in range(4):
                    sp = 0xfffffff8 if value & 1 else 0x1000
                    slot = (sp + saved_offset + byte_index) & MASK
                    gp, s1 = (slot - 82) & MASK, (slot - 7) & MASK
                    memory = {(sp + i) & MASK: (i * 19 + 3) & 255 for i in range(16)}
                    memory[slot] = value
                    before = memory.copy()
                    target, bit, reads = branch.project(branch.CODE, s1, gp, memory)
                    expected_bit = (value >> 1) & 1
                    different = value != expected_bit
                    self.assertEqual(reads, [('read', slot, value), ('read', slot, value)])
                    self.assertEqual((target, bit), (0x103da if different else 0x103f8, expected_bit))
                    def word(offset):
                        return sum(before[(sp + offset + i) & MASK] << (8 * i) for i in range(4))
                    result = tail.execute(destinations[target], target, sp, gp, bit, memory)
                    expected_events = [('read32', (sp + off) & MASK, word(off))
                                       for off in ((8, 12, 4) if different else (12, 8, 4))]
                    if different:
                        expected_events.append(('write8', slot, expected_bit))
                    self.assertEqual(result, ((sp + 16) & MASK, (word(8), word(12), word(4)),
                                              0x13c4e if different else word(12) & ~1, expected_events))
                    if different:
                        before[slot] = expected_bit
                    self.assertEqual(memory, before)
                    counts[int(different)] += 1
        self.assertEqual(counts, [12, 3060])

    def test_changed_branch_target_is_not_an_accepted_tail(self):
        modified = bytearray(branch.CODE)
        modified[12] ^= 0x80
        modified = bytes(modified)
        with patch.object(branch, 'CODE', modified):
            target, _, _ = branch.project(modified, 0x100, 0x1ae, {0x107: 2, 0x200: 1})
        self.assertNotIn(target, (0x103da, 0x103f8))


if __name__ == '__main__':
    unittest.main()
