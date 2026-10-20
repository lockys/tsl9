"""Verify the published local snapshot without network or target execution."""
from pathlib import Path
import hashlib, json, zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'publication-manifest.json').read_text(encoding='utf-8'))
    names = set()
    for row in manifest['files']:
        path = (ROOT / row['path']).resolve()
        assert path.is_relative_to(ROOT) and row['path'] not in names
        names.add(row['path'])
        raw = path.read_bytes()
        assert len(raw) == row['bytes'], row['path']
        assert hashlib.sha256(raw).hexdigest() == row['sha256'], row['path']
    firmware = [r for r in manifest['files'] if r['path'].startswith('firmware-downloads/') and r['path'].endswith('.bin')]
    assert len(firmware) == len({r['sha256'] for r in firmware}) == 22
    apk = ROOT / manifest['APK']['path']
    with zipfile.ZipFile(apk) as archive:
        assert archive.testzip() is None, 'APK member CRC failure'
        assert 'AndroidManifest.xml' in archive.namelist()
    assert not manifest['target_ready'] and not manifest['rebuilt_flashable_BIN']
    print(json.dumps({'passed': True, 'manifest_files': len(names), 'unique_original_BINs': len(firmware), 'APK_SHA256_and_member_CRC': 'passed', 'network': False, 'target_executed': False, 'flashable_rebuild_verified': False}))


if __name__ == '__main__':
    main()
