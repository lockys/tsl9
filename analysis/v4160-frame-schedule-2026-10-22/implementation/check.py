"""Read only the sealed frame-scheduler evidence and optional actual archives."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
MODEL = 'experiments/tsl9-v4160-frame-schedule'


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, default=HERE.parents[2])
    parser.add_argument('--actual-verification', type=Path)
    args = parser.parse_args()
    root = args.project_root.resolve()
    seal = json.loads((HERE / 'seal.json').read_bytes())
    for row in seal['members']:
        path = (HERE / row['path']).resolve()
        need(path.is_relative_to(HERE) and path.stat().st_size == row['bytes'] and sha(path) == row['sha256'], 'Exact evidence member')
    for row in seal['model_members']:
        path = (root / row['path']).resolve()
        need(path.is_relative_to(root) and path.stat().st_size == row['bytes'] and sha(path) == row['sha256'], 'Exact model member')
    audit = root / seal['independent_ABI_seal']['path']
    if not audit.is_file():
        rel = Path(seal['independent_ABI_seal']['path'])
        need(rel.parts[0] == 'analysis', 'Canonical published evidence path')
        audit = root / 'apk-analysis' / ('tsl9-' + rel.parts[1]) / Path(*rel.parts[2:])
    need(sha(audit) == seal['independent_ABI_seal']['sha256'], 'Exact independent frame ABI seal')
    missing_independent_archives = []
    for row in json.loads(audit.read_bytes())['members']:
        path = (audit.parent / row['path']).resolve()
        if not path.is_file():
            need(Path(row['path']).parts[0] == 'build', 'Required independent source/evidence member missing')
            missing_independent_archives.append(row['path'])
            continue
        need(path.is_relative_to(audit.parent) and sha(path) == row['sha256'], 'Exact independent ABI member')
    report = json.loads((HERE / 'verification.json').read_bytes())
    need(report['passed'] and report['fresh_C_CPP_compilation'] is False, 'Archived actual-object evidence, without a fresh compile claim')
    need(len(report['results']) == 2 and all(len(x['actual_receipt_controls']) == 7 for x in report['results']), 'Both languages and seven actual receipt controls')
    actual = False
    if args.actual_verification:
        path = args.actual_verification.resolve()
        need(path.is_relative_to(root), 'Explicit project-local actual verification')
        value = json.loads(path.read_bytes())
        need(value['passed'] and value['driver_sha256'] == sha(root / MODEL / 'verify.py')
             and value['replay_sha256'] == sha(root / MODEL / 'replay.py')
             and value['scheduling_sha256'] == sha(root / MODEL / 'schedule.py'), 'Actual current verification tools')
        sys.path.insert(0, str(root / MODEL))
        spec = importlib.util.spec_from_file_location('frame_receipt_readback', root / MODEL / 'replay.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for row in value['results']:
            need(module.replay(root, root / row['receipt']) == row['positive'], 'Actual complete positive replay')
            for negative in row['actual_receipt_controls']:
                control = (root / row['receipt']).parent / 'controls' / (negative['name'] + '.json')
                need(sha(control) == negative['receipt_sha256'], 'Exact actual negative receipt')
                try:
                    module.replay(root, control)
                except (ValueError, KeyError, IndexError):
                    need(negative['rejected'], 'Recorded rejection')
                else:
                    raise ValueError('Actual negative was accepted')
        actual = True
    print(json.dumps(dict(passed=True, seal_sha256=sha(HERE / 'seal.json'), actual_archives_replayed=actual,
                          independent_build_archives_present=not missing_independent_archives,
                          independent_missing_archive_members=len(missing_independent_archives),
                          independent_actual_archives_replayed=False,
                          fresh_C_CPP_compilation=False, target_execution=False, hardware=False, OTA_ready=False)))


if __name__ == '__main__':
    main()
