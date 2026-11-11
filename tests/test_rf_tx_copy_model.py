import runpy
import unittest

m = runpy.run_path('scripts/rf_tx_copy_model.py')
copy = m['tx_copy']
W = m['POINTER_WORD']
copy_from_word = m['tx_copy_from_word']
load_pointer = m['load_pointer']
provenance = runpy.run_path('scripts/check-rf-copy-provenance.py')


class TxCopyModelTest(unittest.TestCase):
    def memory(self):
        return {a: (a - (W - 16)) & 255 for a in range(W - 16, W + 32)}

    def test_lengths_and_alias_boundaries(self):
        for length in (0, 1, 2, 4):
            for p in range(W - 6, W + 5):
                with self.subTest(length=length, p=hex(p)):
                    before = self.memory()
                    after = copy(before, p, W + 16, length, 0xa5)
                    written = set(range(p, p + 2 + length))
                    self.assertEqual({a for a in before if before[a] != after[a]} - written, set())
                    self.assertEqual(after[p], 0xa5)
                    self.assertEqual(after[p + 1], length)
                    for i in range(length):
                        self.assertEqual(after[p + 2 + i], before[W + 16 + i])
                    self.assertEqual(bool(set(range(p + 2, p + 2 + length)) & set(range(W, W + 4))),
                                     length > 0 and p + 2 < W + 4 and p + 2 + length > W)
                    self.assertEqual(before, self.memory())

    def test_forward_overlap_and_prefix_affect_source(self):
        before = self.memory()
        for i, byte in enumerate((W - 2).to_bytes(4, 'little')):
            before[W + i] = byte
        # The first copy byte reads the length byte; subsequent reads see writes.
        after = copy(before, W - 2, W - 1, 4, 0xa5)
        self.assertEqual([after[W + i] for i in range(4)], [4] * 4)
        self.assertNotEqual([after[W + i] for i in range(4)],
                            [before[W - 1 + i] for i in range(4)])
        self.assertEqual(int.from_bytes(bytes(after[W + i] for i in range(4)), 'little'), 0x04040404)

    def test_self_overwriting_pointer_is_not_reloaded_for_destination(self):
        before = self.memory()
        # P=W: the header stores change W before the helper, but A0 is
        # derived from the original register value, not a fresh load of W.
        for i, b in enumerate(W.to_bytes(4, 'little')):
            before[W + i] = b
        after, initial, reload = copy_from_word(before, W + 16, 2, 0xa5)
        self.assertEqual(initial, W)
        self.assertEqual([after[W + i] for i in range(4)],
                         [0xa5, 2, before[W + 16], before[W + 17]])
        self.assertEqual(reload, load_pointer(after))
        self.assertNotEqual(reload, initial)
        self.assertEqual(load_pointer(before), W)

    def test_prefix_changes_source_but_not_saved_source_address(self):
        before = self.memory()
        for i, b in enumerate((W - 2).to_bytes(4, 'little')):
            before[W + i] = b
        after, initial, reload = copy_from_word(before, W - 1, 4, 0xa5)
        self.assertEqual(initial, W - 2)
        self.assertEqual(reload, 0x04040404)
        self.assertEqual([after[W + i] for i in range(4)], [4] * 4)

    def test_selected_code_window_mutations_rejected_without_image_hash(self):
        bulk = provenance['bulk']
        image = bulk['base']['base']['IMAGE'].read_bytes()
        verify = bulk['base']['verify_windows']
        verify(image)
        # load, branch, both stores, argument setup, call, both later reloads
        for pc in (0x64e0e, 0x64e10, 0x64e14, 0x64e18, 0x64e1a,
                   0x64e1c, 0x64e1e, 0x64e20, 0x64e24, 0x64e28, 0x64e5c):
            with self.subTest(pc=hex(pc)):
                mutated = bytearray(image)
                mutated[pc - 0x40000] ^= 1
                with self.assertRaises(ValueError):
                    verify(mutated)

    def test_reject_invalid_inputs(self):
        before = self.memory()
        for args in ((W, 0, 1, 0), (0xffffffff, W, 0, 0),
                     (W, 0xffffffff, 2, 0), (W, W, -1, 0),
                     (W, W, 1, 1 << 32), (W + 100, W, 1, 0)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                copy(before, *args)
        self.assertEqual(before, self.memory())


if __name__ == '__main__':
    unittest.main()
