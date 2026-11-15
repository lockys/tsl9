#!/usr/bin/env python3
"""Compose 1560e selection and 15630 dispatch at the unknown call boundary.

When the call is made, its returned s2 is injected rather than assumed to
survive. This is static synthetic execution, not an ABI or device claim.
"""
import hashlib
import unittest
import test_155d0_entry_order as entry
import test_1560e_dispatch_guard as guard
import test_1561e_call_boundary as call
import test_15630_dispatch_machine as machine
import test_15630_dispatch_table as table_model

MASK = 0xffffffff


def compose(a0, image, returned_s2=None):
    s2, _, saved_a0, pc = guard.run(guard.CODE, a0)
    called = pc == 0x1561e
    if called:
        args, target, ret = call.decode(call.CODE)
        if (args, target, ret) != ((0x1552a, 0, 20, 0), 0x9124, 0x15630):
            raise ValueError('unexpected call boundary')
        if returned_s2 is None:
            raise ValueError('unknown post-call s2')
        s2 = returned_s2 & MASK
    elif returned_s2 is not None:
        raise ValueError('no call on this path')
    table = image[table_model.BASE - 0x8000:table_model.BASE - 0x8000 + 1012]
    memory = {table_model.BASE + i: b for i, b in enumerate(table)}
    target, events = machine.run(table_model.CODE, memory, s2)
    return called, saved_a0, s2 & 255, target, events


class Composition(unittest.TestCase):
    def test_call_and_skip_paths(self):
        image = entry.BIN.read_bytes()
        self.assertEqual(hashlib.sha256(image).hexdigest(), entry.SHA)
        for addr, code in ((0x1560e, guard.CODE), (0x1561e, call.CODE), (0x15630, table_model.CODE)):
            self.assertEqual(image[addr - 0x8000:addr - 0x8000 + len(code)], code)
        table = image[table_model.BASE - 0x8000:table_model.BASE - 0x8000 + 1012]
        for high in (0, 0x12340000, 0xffffff00):
            for low in range(256):
                a0 = high | low
                s2 = (a0 - 1) & MASK
                called = (s2 & 255) <= 7
                for injected in ((s2, 0xfd) if called else (None,)):
                    result = compose(a0, image, injected)
                    live = injected if called else s2
                    idx, address, target = table_model.dispatch(table_model.CODE, table, live)
                    self.assertEqual(result[:4], (called, a0, idx, target))
                    self.assertEqual(len(result[4]), int(address is not None))
        # An arbitrary post-call clobber can change an otherwise in-range index.
        self.assertNotEqual(compose(1, image, 0)[3], compose(1, image, 253)[3])
        with self.assertRaises(ValueError):
            compose(1, image)
        with self.assertRaises(ValueError):
            compose(10, image, 0)


if __name__ == '__main__':
    unittest.main()
