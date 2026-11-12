"""Verify the published local snapshot without network or target execution."""
from pathlib import Path
import hashlib, json, zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'publication-manifest.json').read_text(encoding='utf-8'))
    names = set()
    for row in manifest['files']:
        path = (ROOT / row['path']).resolve()
        if not (path.is_relative_to(ROOT) and row['path'] not in names):
            raise AssertionError
        names.add(row['path'])
        raw = path.read_bytes()
        if not len(raw) == row['bytes']:
            raise AssertionError(row['path'])
        if not hashlib.sha256(raw).hexdigest() == row['sha256']:
            raise AssertionError(row['path'])
    firmware = [r for r in manifest['files'] if r['path'].startswith('firmware-downloads/') and r['path'].endswith('.bin')]
    if not len(firmware) == len({r['sha256'] for r in firmware}) == 22:
        raise AssertionError
    apk = ROOT / manifest['APK']['path']
    with zipfile.ZipFile(apk) as archive:
        if not archive.testzip() is None:
            raise AssertionError('APK member CRC failure')
        if not 'AndroidManifest.xml' in archive.namelist():
            raise AssertionError
    if not (not manifest['target_ready'] and not manifest['rebuilt_flashable_BIN']):
        raise AssertionError
    print(json.dumps({'passed': True, 'manifest_files': len(names), 'unique_original_BINs': len(firmware), 'APK_SHA256_and_member_CRC': 'passed', 'network': False, 'target_executed': False, 'flashable_rebuild_verified': False}))


if __name__ == '__main__':
    main()
