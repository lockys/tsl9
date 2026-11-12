"""Offline synthetic regression for the publication verifier, including python -O."""
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'verify-publication.py'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def apk_bytes(manifest=True):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_STORED) as archive:
        archive.writestr(zipfile.ZipInfo('AndroidManifest.xml' if manifest else 'other.xml'), b'fake-xml')
    return stream.getvalue()


def fixture(root):
    (root / 'scripts').mkdir()
    (root / 'scripts' / 'verify-publication.py').write_bytes(SCRIPT.read_bytes())
    (root / 'firmware-downloads').mkdir()
    rows = []
    for i in range(22):
        name = 'firmware-downloads/fake%02d.bin' % i
        data = ('fake-%02d' % i).encode('ascii')
        (root / name).write_bytes(data)
        rows.append({'path': name, 'bytes': len(data), 'sha256': digest(data)})
    data = apk_bytes()
    (root / 'fake.apk').write_bytes(data)
    rows.append({'path': 'fake.apk', 'bytes': len(data), 'sha256': digest(data)})
    return {'files': rows, 'APK': {'path': 'fake.apk'}, 'target_ready': False,
            'rebuilt_flashable_BIN': False}


def replace_apk(root, manifest, data):
    (root / 'fake.apk').write_bytes(data)
    row = manifest['files'][-1]
    row['bytes'], row['sha256'] = len(data), digest(data)


def mutate(root, manifest, case):
    rows = manifest['files']
    if case == 'outside':
        rows[0]['path'] = '../outside.bin'
    elif case == 'duplicate_path':
        rows[1] = copy.deepcopy(rows[0])
    elif case == 'size':
        rows[0]['bytes'] += 1
    elif case == 'sha':
        rows[0]['sha256'] = '0' * 64
    elif case == 'count':
        del rows[0]
    elif case == 'unique_sha':
        (root / rows[1]['path']).write_bytes((root / rows[0]['path']).read_bytes())
        rows[1]['sha256'] = rows[0]['sha256']
    elif case == 'crc':
        replace_apk(root, manifest, apk_bytes().replace(b'fake-xml', b'Fake-xml', 1))
    elif case == 'android_manifest':
        replace_apk(root, manifest, apk_bytes(False))
    elif case == 'target_ready':
        manifest['target_ready'] = True
    elif case == 'rebuilt_flashable_BIN':
        manifest['rebuilt_flashable_BIN'] = True
    else:
        raise ValueError(case)


class PublicationOptimizedRegression(unittest.TestCase):
    def test_cli_matrix(self):
        cases = {
            'outside': ('if not (path.is_relative_to(ROOT)', ''),
            'duplicate_path': ('if not (path.is_relative_to(ROOT)', ''),
            'size': ("if not len(raw) == row['bytes']:", 'firmware-downloads/fake00.bin'),
            'sha': ('if not hashlib.sha256(raw).hexdigest()', 'firmware-downloads/fake00.bin'),
            'count': ('if not len(firmware) ==', ''),
            'unique_sha': ('if not len(firmware) ==', ''),
            'crc': ('if not archive.testzip() is None:', 'APK member CRC failure'),
            'android_manifest': ("if not 'AndroidManifest.xml' in archive.namelist():", ''),
            'target_ready': ("if not (not manifest['target_ready']", ''),
            'rebuilt_flashable_BIN': ("if not (not manifest['target_ready']", ''),
        }
        for flags in (['-I', '-S', '-B'], ['-I', '-S', '-O', '-B']):
            for case in ['positive', *cases]:
                with self.subTest(flags=flags, case=case), tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    manifest = fixture(root)
                    if case != 'positive':
                        mutate(root, manifest, case)
                    (root / 'publication-manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
                    script = root / 'scripts' / 'verify-publication.py'
                    result = subprocess.run([sys.executable, *flags, str(script)],
                                            capture_output=True, text=True, timeout=15)
                    if case == 'positive':
                        self.assertEqual(result.returncode, 0, result.stderr)
                        output = json.loads(result.stdout)
                        self.assertEqual(output['unique_original_BINs'], 22)
                        self.assertTrue(output['passed'])
                    else:
                        marker, message = cases[case]
                        lines = script.read_text(encoding='utf-8').splitlines()
                        line = next(i + 2 for i, text in enumerate(lines) if marker in text)
                        self.assertNotEqual(result.returncode, 0, case)
                        self.assertIn('line %d, in main' % line, result.stderr)
                        self.assertEqual(result.stderr.splitlines()[-1],
                                         'AssertionError' + (': ' + message if message else ''))
                        self.assertNotIn('"passed": true', result.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
