#!/usr/bin/env python3
"""Recheck immutable raw source and optional original carrier; no target execution."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def need(value, message):
    if not value:
        raise ValueError(message)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', required=True, type=Path)
    parser.add_argument('--firmware', required=True, type=Path)
    parser.add_argument('--object', type=Path)
    args = parser.parse_args()
    seal = json.loads((HERE / 'seal.json').read_text(encoding='utf-8'))
    for name, expected in seal['members'].items():
        path = (HERE / name).resolve()
        need(path.parent == HERE and digest(path) == expected, 'Sealed member: ' + name)
    spec = importlib.util.spec_from_file_location('page_reply_raw', HERE / 'source-proof.py')
    raw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(raw)
    fresh = raw.inspect(args.project_root.resolve(), args.firmware.resolve(), args.object.resolve() if args.object else None)
    selected = json.loads((HERE / 'source-proof.json').read_text(encoding='utf-8'))
    for key in ('decoded_rows', 'raw_controls', 'retained_roles', 'direct_instruction_written_GPRs', 'raw_body_sha256'):
        need(fresh[key] == selected[key], 'Fresh proof differs: ' + key)
    contract = json.loads((HERE / 'contracts.json').read_text(encoding='utf-8'))
    need(contract['direct_instruction_written_GPRs'] == fresh['direct_instruction_written_GPRs'], 'Direct write contract')
    need(contract['bytes'] == 124 and contract['instructions'] == 50, 'Bounded source contract')
    print(json.dumps({'passed': True, 'bytes': 124, 'instructions': 50, 'raw_operand_controls': 18,
                      'raw_source_rechecked': True, 'selected_original_carrier_was_replayed': selected['actual_carrier_replayed'],
                      'actual_archived_carrier_replayed': fresh['actual_carrier_replayed'],
                      'native_or_host_implementation_tested': False, 'target_execution': False, 'OTA_ready': False}))

if __name__ == '__main__':
    main()
