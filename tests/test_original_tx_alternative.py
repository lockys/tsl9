import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('alternative', ROOT / 'scripts/build-v4160-original-tx-alternative.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
contract_spec = importlib.util.spec_from_file_location('ota_contract', ROOT / 'tests/test_ota_full_image_contract.py')
contract = importlib.util.module_from_spec(contract_spec)
contract_spec.loader.exec_module(contract)


class AlternativeGuardTests(unittest.TestCase):
    def test_full_image_and_reference_mutations_rejected(self):
        ref = (ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')
        if not ref.is_file():
            self.skipTest('local reference unavailable')
        data = ref.read_bytes()
        module.check(data, data)
        for offset in (0, module.START - module.BASE, module.SIZE - 1):
            altered = bytearray(data)
            altered[offset] ^= 1
            with self.assertRaises(ValueError):
                module.check(altered, data)
            with self.assertRaises(ValueError):
                module.check(data, altered)
        with self.assertRaises(ValueError):
            module.check(data[:-1], data)
        with self.assertRaises(ValueError):
            module.check(data, data[:-1])


class IsolatedBuildTests(unittest.TestCase):
    def test_isolated_build_and_missing_inputs(self):
        tool_dir = os.environ.get('TSL9_LLVM_DIR')
        ref = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
        if not tool_dir or not ref.is_file():
            self.skipTest('set TSL9_LLVM_DIR and provide local reference for integration test')
        with tempfile.TemporaryDirectory(prefix='tx-alt-isolation-') as tmp:
            tmp = Path(tmp)
            tree = tmp / 'tree'
            shutil.copytree(ROOT / 'src', tree / 'src', ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.bin', '*.elf', '*.o'))
            (tree / 'scripts').mkdir(parents=True)
            for path in (ROOT / 'scripts').glob('*.py'):
                shutil.copyfile(path, tree / 'scripts' / path.name)
            experiment = tree / 'experiments/tsl9-tx-whole-inline'
            experiment.mkdir(parents=True)
            for name in ('tx.c', 'verify.py'):
                shutil.copyfile(ROOT / 'experiments/tsl9-tx-whole-inline' / name, experiment / name)
            reference = tmp / 'reference.bin'
            shutil.copyfile(ref, reference)
            builder = tree / 'scripts/build-v4160-original-tx-alternative.py'
            def build(name, reference_path):
                out = tmp / name
                p = subprocess.run([sys.executable, '-B', str(builder), '--tool-dir', tool_dir,
                                    '--reference', str(reference_path), '--out', str(out)],
                                   capture_output=True, text=True)
                return out, p
            out, p = build('positive', reference)
            self.assertEqual(p.returncode, 0, p.stderr)
            facts = json.loads(p.stdout)
            self.assertTrue(facts['passed'])
            self.assertFalse(facts['full_source'])
            self.assertTrue(facts['opaque_original_inputs_required'])
            for mode in ('c', 'cpp'):
                image = (out / ('NOT-FLASH-VALIDATED-original-tx-' + mode + '.bin')).read_bytes()
                baseline = (out / 'baseline' / ('NOT-FLASH-VALIDATED-v4160-source-' + mode + '.bin')).read_bytes()
                tx = (out / ('tx-' + mode + '.bin')).read_bytes()
                start, end = module.START - module.BASE, module.END - module.BASE
                self.assertEqual(image, baseline[:start] + tx + baseline[end:])
                self.assertNotEqual(tx, baseline[start:end])
                self.assertEqual(image, reference.read_bytes())
                self.assertEqual(contract.pinned_image(out / ('NOT-FLASH-VALIDATED-original-tx-' + mode + '.bin'), contract.SHA_OFFICIAL), image)
                chunks = contract.pages(image)
                contract.check_pages(chunks, 75, 76950, 31872)
                for metadata in ((74, 76950, 31872), (75, 76949, 31872), (75, 76950, 31873)):
                    with self.assertRaises(ValueError):
                        contract.check_pages(chunks, *metadata)
                self.assertEqual(b''.join(page[2:] for page in chunks), image)
                for page in chunks:
                    self.assertEqual(contract.check_frame(contract.frame(87, page)), (87, page))
                for bad in (chunks[:-1], chunks + [chunks[-1]], [chunks[1], chunks[0]] + chunks[2:]):
                    with self.assertRaises(ValueError):
                        contract.check_pages(bad, 75, 76950, 31872)
                wire = contract.frame(87, chunks[0])
                for bad in (wire[:-1], b'\x54' + wire[1:], wire[:-1] + bytes([wire[-1] ^ 1])):
                    with self.assertRaises(ValueError):
                        contract.check_frame(bad)
            missing_out, p = build('missing-reference', tmp / 'absent.bin')
            self.assertNotEqual(p.returncode, 0)
            self.assertFalse(missing_out.exists())
            stale = tmp / 'stale-reference.bin'
            data = bytearray(reference.read_bytes())
            data[-1] ^= 1
            stale.write_bytes(data)
            stale_out, p = build('stale-reference', stale)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn('reference size or SHA-256 mismatch', p.stderr)
            self.assertFalse(stale_out.exists())
            payload = tree / 'src/native/tx_candidate/full-image-payload.json'
            payload_bytes = payload.read_bytes()
            payload.unlink()
            missing_out, p = build('missing-payload', reference)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn('full-image-payload.json', p.stderr)
            self.assertFalse(list(missing_out.glob('NOT-FLASH-VALIDATED-original-tx-*.bin')))
            payload.write_bytes(payload_bytes)
            source = experiment / 'tx.c'
            text = source.read_text(encoding='utf-8')
            self.assertEqual(text.count('addi a5, zero, 1039'), 1)
            source.write_text(text.replace('addi a5, zero, 1039', 'addi a5, zero, 1038'), encoding='utf-8')
            missing_out, p = build('mutated-source', reference)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn('byte mismatch', p.stderr)
            self.assertFalse(list(missing_out.glob('NOT-FLASH-VALIDATED-original-tx-*.bin')))


if __name__ == '__main__':
    unittest.main()
