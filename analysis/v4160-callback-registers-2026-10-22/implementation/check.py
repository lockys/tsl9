#!/usr/bin/env python3
"""Check sealed source/selected metadata, optionally replay explicit actual outputs."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def need(value, message):
    if not value:
        raise ValueError(message)


def inspect(root, receipt=None, require_local=False):
    seal = json.loads((HERE / 'seal.json').read_bytes())
    for directory, members in ((HERE, seal['members']),
                               (root / 'experiments/tsl9-v4160-callback-registers', seal['model_members'])):
        for name, pin in members.items():
            path = (directory / name).resolve()
            need(path.is_relative_to(directory) and path.is_file() and sha(path) == pin,
                 'Exact sealed source/metadata member ' + name)
    need(sha(root / 'experiments/tsl9-v4160-callback-registers/postpass/frame.py') == seal['frame_pass_sha256'],
         'Parent-owned frozen save-order dependency')
    for independent in seal['independent_seals']:
        directory = next(p for p in (root / 'analysis' / independent['case'],
                                      root / 'apk-analysis' / ('tsl9-' + independent['case'])) if p.is_dir())
        need(sha(directory / independent['scope'] / 'seal.json') == independent['sha256'],
             'Exact independently closed review seal')
    source = runpy.run_path(str(HERE / 'source_gate.py'))['inspect'](root)
    results = json.loads((HERE / 'results.json').read_bytes())
    need(len(results['results']) == 2 and [r['mode'] for r in results['results']] == ['c', 'cpp'],
         'Exactly two selected formal language receipts')
    for selected in results['results']:
        metadata = HERE / selected['metadata']
        need(sha(metadata) == selected['sha256'], 'Byte-identical selected formal metadata')
        record = json.loads(metadata.read_bytes())
        need(record['passed'] and record['mode'] == selected['mode'] and
             record['checks']['after']['bytes'] == 624 and record['checks']['after']['instructions'] == 223 and
             record['checks']['after']['relative_source_save_order_preserved'] and
             not record['original_ABI_admitted'] and not record['original_placement_admitted'],
             'Selected metadata has precise partial admission scope')
    actual = []
    if receipt or require_local:
        runner = runpy.run_path(str(HERE / 'verify_native.py'))
        for selected in ([receipt] if receipt else [Path(r['receipt']) for r in results['results']]):
            actual.append(runner['replay'](root, selected))
    return dict(passed=True, sealed_members=len(seal['members']), model_members=len(seal['model_members']), source_refinement=source,
                selected_metadata_receipts=2, actual_native_artifacts_read=bool(actual),
                actual_replays=actual, original_ABI_admitted=False, original_placement_admitted=False,
                target_execution=False, HOST_tests_rerun=False, BIN_exported=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', required=True, type=Path)
    parser.add_argument('--receipt', type=Path)
    parser.add_argument('--require-local-builds', action='store_true')
    args = parser.parse_args()
    need(not (args.receipt and args.require_local_builds), 'One explicit actual replay mode')
    print(json.dumps(inspect(args.project_root.resolve(), args.receipt, args.require_local_builds)))
