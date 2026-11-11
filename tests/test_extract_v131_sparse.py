import importlib.util
import os
import runpy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/extract_v131_sparse.py'
spec = importlib.util.spec_from_file_location('sparse_evidence', ROOT / 'scripts/sparse_resident_evidence.py')
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)


def record(addr, typ, data=b''):
    body = bytes([len(data), addr >> 8, addr & 255, typ]) + data
    return ':' + (body + bytes([-sum(body) & 255])).hex().upper()


class ParserTests(unittest.TestCase):
    def test_adversarial_records(self):
        parse = runpy.run_path(str(ROOT / 'analysis/v131-startup-source/check.py'))['parse']
        eof = record(0, 1)
        data = record(0, 0, b'\x12')
        self.assertEqual(parse((data + '\r\n' + eof + '\r\n').encode()), {0: 0x12})
        bad = {
            'whitespace': data[:3] + ' ' + data[3:] + '\n' + eof,
            'vertical tab': data + '\v' + eof,
            'missing eof': data,
            'after eof': eof + '\n' + data,
            'duplicate': data + '\n' + data + '\n' + eof,
            'checksum': data[:-2] + '00\n' + eof,
            'length': ':0200000012EC\n' + eof,
            'unknown': record(0, 6) + '\n' + eof,
            'bad eof': record(1, 1) + '\n' + eof,
            'cross 64k': record(0xffff, 0, b'\x00\x01') + '\n' + eof,
            'overflow 32bit': record(0, 4, b'\xff\xff') + '\n' + record(0xffff, 0, b'\x00\x01') + '\n' + eof,
        }
        for name, text in bad.items():
            with self.subTest(name=name), self.assertRaises(ValueError):
                parse(text.encode())


class ExtractionTests(unittest.TestCase):
    def test_offline_roundtrip_and_negative_controls(self):
        source = Path(os.environ.get('V131_HEX', ROOT / 'analysis/v131-startup-source/wchble_rom.hex')).resolve()
        if not source.is_file():
            self.skipTest('set V131_HEX to the pinned locally obtained HEX')
        raw = source.read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            def run(src, out):
                return subprocess.run([sys.executable, *(['-O'] if sys.flags.optimize else []), '-B', str(SCRIPT), '--hex', str(src), '--out', str(out)], capture_output=True)
            one, two = base / 'one', base / 'two'
            self.assertEqual(run(source, one).returncode, 0)
            self.assertEqual(run(source, two).returncode, 0)
            self.assertEqual({p.name: p.read_bytes() for p in one.iterdir()}, {p.name: p.read_bytes() for p in two.iterdir()})
            segments = evidence.validate(ROOT, one.resolve(), source)
            self.assertEqual(len(segments), 17)
            self.assertEqual(segments[-1]['end_exclusive'], 0x6eb2c)
            self.assertNotEqual(run(source, one).returncode, 0)
            (base / 'input').mkdir()
            bad = base / 'input' / 'bad.hex'
            bad.write_bytes(raw[:-1] + bytes([raw[-1] ^ 1]))
            self.assertNotEqual(run(bad, base / 'bad-output').returncode, 0)
            self.assertFalse((base / 'bad-output').exists())
            segment = one / segments[-1]['path']
            segment.write_bytes(segment.read_bytes() + b'\0')
            with self.assertRaises(ValueError):
                evidence.validate(ROOT, one.resolve(), source)
            manifest = two / 'source-map.json'
            manifest.write_bytes(manifest.read_bytes().replace(b'"passed": true', b'"passed": false'))
            with self.assertRaises(ValueError):
                evidence.validate(ROOT, two.resolve(), source)
            self.assertNotEqual(run(source, ROOT / 'no-output-allowed').returncode, 0)
            self.assertEqual(source.read_bytes(), raw)


if __name__ == '__main__':
    unittest.main()
