"""Real decoder/persistence with an offline HTTP boundary double; no sockets."""
from pathlib import Path
import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'download_firmware.py'
SPEC = importlib.util.spec_from_file_location('portable_download', SCRIPT)
COMPONENT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COMPONENT)
SYNTHETIC = '00112233445566778899AABB'
MARKER = '接收OK'.encode('utf-8')
PAYLOAD = bytes(range(256)) * 4
LINE = bytes(x ^ 0xB7 for x in PAYLOAD).hex().encode('ascii')


class DownloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state = {}
        cls.requests = []
        class Response:
            def __init__(self):
                self.status = cls.state.get('status', 200)
                self.body = cls.state.get('body', LINE + MARKER)
            def getheader(self, name):
                return str(cls.state.get('length', len(self.body))) if name == 'Content-Length' else None
            def read(self, maximum):
                return self.body[:maximum]
        class Connection:
            def __init__(self, host, port, timeout):
                cls.host = host
            def request(self, method, path, body, headers):
                from urllib.parse import parse_qs, urlsplit
                if method != 'POST' or headers['Content-Type'] != 'application/x-www-form-urlencoded':
                    raise AssertionError('request contract')
                cls.requests.append((urlsplit(path), parse_qs(body.decode('ascii'))))
            def getresponse(self):
                return Response()
            def close(self):
                pass
        cls.connection = Connection
        cls.url = 'http://127.0.0.1:12345/ffkj/user/'

    def setUp(self):
        scratch = ROOT / 'scratch'
        scratch.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.root = Path(self.temp.name)
        self.assertEqual(self.root.resolve().parent, scratch.resolve())
        self.addCleanup(self.temp.cleanup)
        self.catalog = self.root / 'catalog.json'
        self.catalog.write_text(json.dumps({'options': [{'FirmwareID': 2966, 'version_labels': ['V4.1.60']}]}), encoding='utf-8')
        self.out = self.root / 'outputs'
        self.state.clear()
        self.requests.clear()

    def run_cli(self, *extra):
        argv = ['--firmware-id', '2966', '--options-receipt', str(self.catalog), '--output-root', str(self.out), *extra]
        if '--dry-run' in extra:
            r = subprocess.run([sys.executable, '-B', str(SCRIPT), *argv], capture_output=True, timeout=10)
            self.assertNotIn(SYNTHETIC.encode(), r.stdout + r.stderr)
            self.assertEqual(r.stderr, b'', r.stderr)
            return r, json.loads(r.stdout)
        output = io.StringIO()
        with patch.object(COMPONENT.http.client, 'HTTPConnection', self.connection), contextlib.redirect_stdout(output):
            status = COMPONENT.main(argv)
        self.assertNotIn(SYNTHETIC, output.getvalue())
        return SimpleNamespace(returncode=status), json.loads(output.getvalue())

    def test_dry_run_has_no_network_or_output(self):
        r, report = self.run_cli('--dry-run')
        self.assertEqual(r.returncode, 0, report)
        self.assertEqual(report['request_attempts'], 0)
        self.assertFalse(report['target_ready'])
        self.assertFalse(self.requests)
        self.assertFalse(self.out.exists())

    def test_valid_pages_are_decoded_create_only_and_hash_bound(self):
        import hashlib
        from urllib.parse import parse_qs
        for pages, trailing in [(1, False), (2, True)]:
            with self.subTest(pages=pages):
                self.requests.clear()
                self.state['body'] = b'\r\n'.join([LINE] * pages) + (b'\r\n' if trailing else b'') + MARKER
                r, report = self.run_cli('--mock-uri', self.url)
                self.assertEqual(r.returncode, 0, report)
                self.assertEqual(len(self.requests), 1)
                url, fields = self.requests[0]
                self.assertEqual(url.path, '/ffkj/user/')
                self.assertEqual(set(parse_qs(url.query)), {'Temp'})
                self.assertEqual(fields, {'action': ['GetFirmware'], 'f_UID': [SYNTHETIC], 'f_FirmwareID': ['2966'], 'ver': ['30']})
                folder = Path(report['directory'])
                self.assertEqual(Path(report['bin']).read_bytes(), PAYLOAD * pages)
                receipt = json.loads((folder / 'receipt.json').read_text(encoding='utf-8'))
                self.assertFalse(receipt['uid_stored'])
                self.assertTrue(receipt['mock'])
                for name, info in receipt['files'].items():
                    raw = (folder / name).read_bytes()
                    self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()), (info['bytes'], info['sha256']))
                self.assertEqual((folder / 'download.hex').read_bytes(), (LINE + b'\r\n') * pages)

    def test_rejections_never_save_reply_follow_redirect_or_retry(self):
        cases = [
            ('redirect', {'status': 302}), ('forbidden', {'status': 403}), ('limited', {'status': 429}),
            ('bad_utf8', {'body': b'\xff' + MARKER}), ('missing_marker', {'body': LINE}),
            ('duplicate_marker', {'body': LINE + MARKER + MARKER}),
            ('bare_lf', {'body': LINE + b'\n' + LINE + MARKER}),
            ('short_page', {'body': b'0000' + MARKER}),
            ('nonhex_secret_body', {'body': SYNTHETIC.encode() + MARKER}),
            ('97_pages', {'body': b'\r\n'.join([LINE] * 97) + MARKER}),
            ('oversized_header', {'body': b'', 'length': 262145}),
        ]
        for name, state in cases:
            with self.subTest(case=name):
                self.state.clear(); self.state.update(state); self.requests.clear()
                r, report = self.run_cli('--mock-uri', self.url)
                self.assertNotEqual(r.returncode, 0)
                self.assertEqual(report['status'], 'stopped')
                self.assertEqual(report['request_attempts'], 1)
                self.assertEqual(report['retries'], 0)
                self.assertEqual(len(self.requests), 1)
                self.assertFalse(self.out.exists())

    def test_unknown_id_and_duplicate_catalog_stop_before_request(self):
        for options in [[], [{'FirmwareID': 2966}, {'FirmwareID': 2966}]]:
            with self.subTest(options=len(options)):
                self.catalog.write_text(json.dumps({'options': options}), encoding='utf-8')
                r, report = self.run_cli('--mock-uri', self.url)
                self.assertNotEqual(r.returncode, 0)
                self.assertEqual(report['request_attempts'], 0)
                self.assertFalse(self.requests)
                self.assertFalse(self.out.exists())

    def test_nonliteral_nonloopback_and_ambiguous_urls_stop_before_request(self):
        for url in ['http://localhost/', 'http://192.0.2.1/', 'https://127.0.0.1/', 'http://127.0.0.1/?x=1', 'http://user@127.0.0.1/', 'http://127.0.0.1/#x', 'http://127.0.0.1:0/']:
            with self.subTest(url=url):
                r, report = self.run_cli('--mock-uri', url)
                self.assertNotEqual(r.returncode, 0)
                self.assertEqual(report['request_attempts'], 0)
                self.assertFalse(self.requests)
                self.assertFalse(self.out.exists())


if __name__ == '__main__':
    unittest.main()
