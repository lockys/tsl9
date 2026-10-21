#!/usr/bin/env python3
"""Check this bounded ABI-order archive; optionally replay actual ELF artifacts."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODEL = 'experiments/tsl9-v4160-reply-abi-order'
MODEL_FILES = ['.gitignore', 'README.md', 'order-policy.json', 'order.py',
               'readme.en.md', 'readme.zh-TW.md', 'verify.sh']
CASE_FILES = ['audit-c.json', 'audit-cpp.json', 'check-seal.py', 'record.py', 'verification.json']


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def members(root):
    return [(name, root / MODEL / name, 'model') for name in MODEL_FILES] + [
        (name, HERE / name, 'case') for name in CASE_FILES]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', type=Path, required=True)
    p.add_argument('--seal', action='store_true')
    p.add_argument('--receipt', type=Path)
    a = p.parse_args()
    root = a.project_root.resolve()
    items = [dict(path=name, scope=scope, bytes=path.stat().st_size, sha256=sha(path))
             for name, path, scope in members(root)]
    value = dict(schema='TSL9-standalone-page-reply-ABI-order-seal-v1',
                 members=items, model=MODEL, hardware=False, OTA_ready=False)
    seal = HERE / 'seal.json'
    if a.seal:
        need(a.receipt is None and not seal.exists(), 'Create-only metadata seal')
        with seal.open('xb') as out:
            out.write((json.dumps(value, indent=2) + '\n').encode())
    else:
        need(json.loads(seal.read_bytes()) == value, 'Exact member set / bytes / digests')
    need((root / MODEL / 'README.md').read_bytes() ==
         (root / MODEL / 'readme.zh-TW.md').read_bytes(), 'Full TW README equality')
    report = json.loads((HERE / 'verification.json').read_bytes())
    need(report['passed'] and len(report['languages']) == 2,
         'Complete archived C and C++ verification summaries')
    result = dict(passed=True, members=len(items), seal_sha256=sha(seal),
                  archived_verification_bound=True, actual_ELF_replay=False,
                  target_execution=False, ISA_emulation=False, OTA_ready=False)
    if a.receipt:
        checker = runpy.run_path(str(root / MODEL / 'order.py'))
        current = checker['replay'](root, a.receipt)
        result.update(actual_ELF_replay=True,
                      changed_bytes=len(current['proof']['changed_file_offsets']))
    print(json.dumps(result))


if __name__ == '__main__':
    main()
