#!/usr/bin/env python3
"""Default metadata-only seal check; optional actual archive replays are explicit."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys
sys.dont_write_bytecode = True
MODEL = 'experiments/tsl9-v4160-ota-handler-compact'

def H(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def need(condition, message):
    if not condition:
        raise ValueError(message)

def case_at(root):
    return next(p for p in (root/'analysis/v4160-ota-handler-compact-2026-10-22', root/'apk-analysis/tsl9-v4160-ota-handler-compact-2026-10-22') if p.is_dir())

def check(root, host=(), native=()):
    scope = case_at(root)/'implementation'
    seal = json.loads((scope/'seal.json').read_bytes())
    for base, key in ((scope, 'members'), (root/MODEL, 'model_members')):
        for name, pin in seal[key].items():
            path = (base/name).resolve()
            need(path.is_relative_to(base.resolve()) and H(path) == pin, 'Exact sealed member '+name)
    for item in seal['dependencies']:
        path = next((root/name for name in item['paths'] if (root/name).is_file()), None)
        need(path is not None and H(path) == item['sha256'], 'Exact portable dependency '+item['paths'][0])
    for item in seal['independent_seals']:
        path = case_at(root)/item['scope']/'seal.json'
        need(H(path) == item['sha256'], 'Exact independent seal '+item['scope'])
        independent = json.loads(path.read_bytes())
        members = independent.get('members') or {row['path']: row['sha256'] for row in independent['files']}
        for name, pin in members.items():
            member = (path.parent/name).resolve()
            need(member.is_relative_to(path.parent.resolve()) and H(member) == pin, 'Independent sealed member '+name)
    index = json.loads((scope/'results.json').read_bytes())
    need(len(index['results']) == 4, 'Exactly four selected formal metadata receipts')
    for item in index['results']:
        path = scope/item['metadata']
        need(H(path) == item['sha256'], 'Byte-identical selected receipt metadata')
        data = json.loads(path.read_bytes())
        need(data['passed'] and data['mode'] == item['mode'], 'Formal language/status')
        if item['kind'] == 'host':
            need(data['tests'] == dict(groups=1, cases=10, checks=8292) and len(data['compiled_controls']) == 3, 'Exact HOST suite metadata')
        else:
            need(data['checks']['native_bytes'] == 568 and data['checks']['instructions'] == 193 and not data['checks']['original_ABI_admitted'], 'Exact partial native metadata')
    checks = []
    for receipt in host:
        checks.append(runpy.run_path(str(root/MODEL/'verify_host.py'))['replay'](root, receipt))
    for receipt in native:
        checks.append(runpy.run_path(str(scope/'verify_native.py'))['replay'](root, receipt))
    return dict(passed=True, metadata_only=not(host or native), actual_host_archives_read=bool(host), actual_native_artifacts_read=bool(native), replays=checks, native_bytes=568, original_bytes=530, original_ABI_admitted=False, original_placement_admitted=False, BIN_exported=False, target_execution=False, hardware_OTA_proved=False)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--host-receipt', action='append', type=Path, default=[])
    parser.add_argument('--native-receipt', action='append', type=Path, default=[])
    args = parser.parse_args()
    print(json.dumps(check(args.project_root.resolve(), args.host_receipt, args.native_receipt)))

if __name__ == '__main__':
    main()
