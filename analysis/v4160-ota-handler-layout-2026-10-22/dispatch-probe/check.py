#!/usr/bin/env python3
"""Metadata-only negative experiment check, or explicit actual archive replay."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
CODE = 'b486c6eed0d3465c8947fd338e790f1441f29c64827a47b20e1fada18ff863af'

def H(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def need(value, message):
    if not value:
        raise ValueError(message)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    root = args.project_root.resolve()
    seal = json.loads((HERE/'seal.json').read_bytes())
    for name, pin in seal['members'].items():
        path = (HERE/name).resolve()
        need(path.is_relative_to(HERE) and H(path) == pin, 'Exact evidence member '+name)
    for name, pin in seal['baseline_sources'].items():
        need(H(root/'experiments/tsl9-v4160-ota-handler-compact/src'/name) == pin, 'Unchanged source baseline '+name)
    result = json.loads((HERE/'results.json').read_bytes())
    need(result['negative_result'] and not result['promoted_model'], 'Negative outcome without promotion')
    for item in result['results']:
        path = HERE/item['metadata']
        need(H(path) == item['sha256'], 'Selected actual receipt metadata identity')
        record = json.loads(path.read_bytes())
        checks = record['checks']
        need(checks['native_bytes'] == 568 and checks['instructions'] == 193 and checks['code_sha256'] == CODE, 'Measured unchanged native payload')
    replay = None
    if args.receipt:
        replay = runpy.run_path(str(HERE/'probe.py'))['replay'](root, args.receipt)
    print(json.dumps(dict(passed=True, metadata_only=args.receipt is None,
                          actual_native_artifacts_read=args.receipt is not None,
                          negative_result=True, promoted_model=False, native_bytes=568,
                          payload_equal_to_baseline=True, replay=replay,
                          original_ABI_admitted=False, original_placement_admitted=False,
                          linked=False, BIN_exported=False, target_execution=False)))

if __name__ == '__main__':
    main()
