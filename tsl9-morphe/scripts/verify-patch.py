"""Independent APK/wxapkg verifier; never executes APK or prints its JS/config."""
import hashlib
import json
import struct
import sys
import zipfile
from pathlib import Path

EXPECTED_APK = '10d7d92f16d7806d841fcfd152b318601f6c234a2445e99e0729709aacc9c3ee'


def unpack(data):
    assert data[0] == 0xBE and data[13] == 0xED, 'Bad wxapkg markers'
    _, index_size, body_size = struct.unpack_from('>III', data, 1)
    assert len(data) == 14 + index_size + body_size, 'Bad wxapkg size'
    count = struct.unpack_from('>I', data, 14)[0]
    cursor, files = 18, {}
    for _ in range(count):
        length = struct.unpack_from('>I', data, cursor)[0]
        cursor += 4
        name = data[cursor:cursor + length].decode('utf-8')
        cursor += length
        offset, size = struct.unpack_from('>II', data, cursor)
        cursor += 8
        assert name not in files, 'Duplicate path'
        assert offset >= 14 + index_size and offset + size <= len(data), 'Bad range'
        files[name] = (offset, size, data[offset:offset + size])
    assert cursor == 14 + index_size, 'Bad index boundary'
    return files


def main():
    original_path, patched_path = map(Path, sys.argv[1:3])
    assert hashlib.sha256(original_path.read_bytes()).hexdigest() == EXPECTED_APK
    with zipfile.ZipFile(original_path) as original, zipfile.ZipFile(patched_path) as patched:
        assert original.testzip() is None and patched.testzip() is None
        original_names, patched_names = set(original.namelist()), set(patched.namelist())
        content_names = {n for n in original_names if not n.startswith('META-INF/') and not n.endswith('/')}
        assert content_names == {n for n in patched_names if not n.startswith('META-INF/') and not n.endswith('/')}, 'APK payload entry set changed'
        changed = [n for n in sorted(content_names) if original.read(n) != patched.read(n)]
        assert len(changed) == 1 and changed[0].endswith('.wxapkg'), 'Unexpected APK content changes'
        before, after = original.read(changed[0]), patched.read(changed[0])
        old_files, new_files = unpack(before), unpack(after)
        assert old_files.keys() == new_files.keys()
        modified = [n for n in old_files if old_files[n][2] != new_files[n][2]]
        assert modified == ['/app-config.json'], 'Unexpected miniapp changes'
        old, new = old_files[modified[0]][2], new_files[modified[0]][2]
        old_json, new_json = json.loads(old), json.loads(new)
        assert old_json['tabBar']['list'][0]['text'] == '\u72b6\u6001'
        assert new_json['tabBar']['list'][0]['text'] == '\u72c0\u614b\u00b7M'
        new_json['tabBar']['list'][0]['text'] = old_json['tabBar']['list'][0]['text']
        assert old_json == new_json, 'Other JSON fields changed'
        delta = len(new) - len(old)
        target_end = old_files[modified[0]][0] + len(old)
        for name, (offset, size, _) in old_files.items():
            expected_offset = offset + (delta if offset >= target_end else 0)
            assert new_files[name][0] == expected_offset, 'Unexpected relocated offset'
            assert new_files[name][1] == size + (delta if name == modified[0] else 0)
        result = dict(status='PASS', apk_payload_changes=changed, miniapp_changes=modified,
                      wxapkg_entries=len(new_files), size_delta=delta,
                      original_sha256=EXPECTED_APK,
                      patched_sha256=hashlib.sha256(patched_path.read_bytes()).hexdigest(),
                      dex_and_manifest_identical=True, runtime_verified=False)
        print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
