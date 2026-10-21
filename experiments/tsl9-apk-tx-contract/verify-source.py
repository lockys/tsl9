"""Portable read-only APK chain/range verifier; no JavaScript evaluation."""
import argparse
import hashlib
import json
import struct
import zipfile
from pathlib import Path


def sha(b):
    return hashlib.sha256(b).hexdigest()


def need(value, message):
    if not value:
        raise AssertionError(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apk', type=Path, required=True)
    parser.add_argument('--proof-root', type=Path, required=True)
    parser.add_argument('--rx-root', type=Path, required=True)
    args = parser.parse_args()
    scope = Path(__file__).resolve().parent
    pins = json.loads((scope/'source-map.json').read_text(encoding='utf8'))
    sealed = {}
    for name, digest in pins['proof_seals'].items():
        path = args.proof_root/name
        data = path.read_bytes()
        need(sha(data) == digest, 'exact sealed source proof '+name)
        seal = json.loads(data)
        need(seal['passed'], 'source proof passed '+name)
        for member in seal['members']:
            item = (path.parent/member['path']).resolve()
            need(item.is_relative_to(path.parent.resolve()), 'contained proof member')
            b = item.read_bytes()
            need(len(b) == member['bytes'] and sha(b) == member['sha256'],
                 'sealed member '+member['path'])
            sealed[str(item)] = sha(b)
        sealed[str(path.resolve())] = digest
    for name, digest in pins['receive_inputs'].items():
        data = (args.rx_root/name).read_bytes()
        need(sha(data) == digest, 'original bounded receiver '+name)
    need(sha(args.apk.read_bytes()) == pins['apk_sha256'], 'original APK')
    with zipfile.ZipFile(args.apk) as z:
        pkg = z.read('assets/SaaA_embed/release_2_wx64f19032ca1ea79e.wxapkg')
    need(sha(pkg) == pins['wxapkg_sha256'] and pkg[0] == 190 and pkg[13] == 237,
         'wxapkg identity/header')
    index_bytes, body_bytes = struct.unpack_from('>II', pkg, 5)
    count = struct.unpack_from('>I', pkg, 14)[0]
    at, entries = 18, {}
    for _ in range(count):
        n = struct.unpack_from('>I', pkg, at)[0]
        at += 4
        name = pkg[at:at+n].decode('utf8')
        at += n
        offset, size = struct.unpack_from('>II', pkg, at)
        at += 8
        need(name not in entries and offset >= 14+index_bytes
             and offset+size <= len(pkg), 'bounded unique package entry')
        entries[name] = (offset, size)
    need(count == 76 and at == 14+index_bytes and 14+index_bytes+body_bytes == len(pkg),
         'exact package extent')
    offset, size = entries['/appservice.app.js']
    raw = pkg[offset:offset+size]
    need(sha(raw) == pins['appservice_sha256'], 'appservice identity')
    app = raw.decode('utf8')
    sender_bytes = (args.proof_root/'tx-source/exact-source.json').read_bytes()
    need(sha(sender_bytes) == pins['sender_fixture_sha256'], 'sender fixture identity')
    sender = json.loads(sender_bytes)
    receiver = json.loads((args.rx_root/'source-map.json').read_text(encoding='utf8'))
    rows = sender['sections']+receiver['sections']
    for row in rows:
        start, end = row['original_start_codepoint'], row['original_end_codepoint']
        text = app[start:end]
        b = text.encode('utf8')
        need(text == row['source_utf8'] and len(b) == row['source_bytes']
             and sha(b) == row['sha256'], 'original inert source '+row['name'])
        need(app.count('\n', 0, start)+1 == row['original_line'], 'original line')
    print(json.dumps(dict(passed=True, sender_sections=len(sender['sections']),
        receiver_sections=len(receiver['sections']), sealed_files=len(sealed),
        sealed_inputs=sealed, apk_sha256=pins['apk_sha256'],
        original_executed=False, network=False, BLE=False, hardware=False)))


if __name__ == '__main__':
    main()
