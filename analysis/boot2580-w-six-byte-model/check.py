"""Hand-derived, offline state-transition model; not an ISA emulator."""
from pathlib import Path
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[2]
FRAME = bytes.fromhex('55 7f 57 00 00 57')

class State:
    def __init__(self):
        self.buf = FRAME
        self.length = 6
        self.offset = 0
        self.chunk = None
        self.tries = 0

    def prepare(self, cfg, capacity):
        # The two halfwords are loaded before the cfg provider is called.
        diff = (self.length - self.offset) & 0xffff
        signed = diff if diff < 0x8000 else diff - 0x10000
        if cfg != 1 or signed <= 0:
            self.length = 0
            return False
        self.chunk = min(signed, (capacity - 3) & 0xffff)
        self.tries = 10
        return True

    def attempt(self, alloc=True, cfg=1, submit=0):
        assert self.chunk is not None
        if self.tries == 0:
            self.length = 0
            return ('exhausted', None)
        if not alloc:
            self.tries = (self.tries - 1) & 255
            return ('retry', None)
        # Snapshot expresses the copy call's requested source, not provider effects.
        copied = self.buf[self.offset:self.offset + self.chunk]
        if cfg & 1 and submit == 0:
            self.offset = (self.offset + self.chunk) & 0xffff
            return ('advance', copied)
        self.tries = (self.tries - 1) & 255
        return ('retry', copied)

class Tests(unittest.TestCase):
    def test_fragment_and_completion(self):
        s = State(); parts = []
        for offset, size in [(0, 4), (4, 2)]:
            self.assertEqual(s.offset, offset)
            self.assertTrue(s.prepare(1, 7))
            self.assertEqual(s.chunk, size)
            status, data = s.attempt()
            self.assertEqual(status, 'advance'); parts.append(data)
        self.assertEqual(b''.join(parts), FRAME)
        self.assertFalse(s.prepare(1, 7)); self.assertEqual(s.length, 0)
        self.assertEqual(s.offset, 6)

    def test_boundaries(self):
        for capacity, size in [(3, 0), (4, 1), (9, 6), (2, 6)]:
            s = State(); self.assertTrue(s.prepare(1, capacity)); self.assertEqual(s.chunk, size)
        s = State(); self.assertFalse(s.prepare(3, 9)); self.assertEqual(s.length, 0)
        s = State(); s.offset = 7; self.assertFalse(s.prepare(1, 9))
        s = State(); s.offset = 0x8006; self.assertFalse(s.prepare(1, 9))

    def test_retry_and_exhaustion(self):
        s = State(); s.prepare(1, 7)
        for i in range(10):
            status, _ = s.attempt(alloc=False)
            self.assertEqual(status, 'retry'); self.assertEqual(s.offset, 0)
            self.assertEqual(s.tries, 9-i)
        self.assertEqual(s.attempt()[0], 'exhausted'); self.assertEqual(s.length, 0)
        s = State(); s.prepare(1, 7)
        for cfg, submit in [(0, 0), (1, 4), (2, 0)]:
            self.assertEqual(s.attempt(cfg=cfg, submit=submit)[0], 'retry')
            self.assertEqual(s.offset, 0)
        self.assertEqual(s.attempt(cfg=3, submit=0), ('advance', FRAME[:4]))

    def test_interleavings_are_not_atomic(self):
        s = State(); s.prepare(1, 7)
        self.assertEqual(s.attempt(submit=1)[1], FRAME[:4])
        s.buf = b'ABCDEF'; s.offset = 1  # competing writer before retry
        self.assertEqual(s.attempt(), ('advance', b'BCDE'))
        self.assertEqual(s.offset, 5)
        s = State(); s.prepare(1, 7)
        s.buf = b'ABCDEF'; s.offset = 0; s.length = 6  # another wrapper
        self.assertEqual(s.attempt()[1], b'ABCD')
        self.assertEqual(s.offset, 4)  # old chunk applied to new frame

if __name__ == '__main__':
    # Independent existing gates pin the complete original image and relevant windows.
    for name in ('boot2580-w-wrapper-offline', 'boot2580-w-event-continuation', 'boot2580-w-event-return-offline'):
        import subprocess, sys
        subprocess.run([sys.executable, '-B', str(ROOT / 'analysis' / name / 'check.py')], check=True)
    unittest.main()
