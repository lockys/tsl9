#!/usr/bin/env python3
"""Archive actual prototype byte/readback checks, never compile or run RV32."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODEL = 'experiments/tsl9-v4160-reply-abi-order'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def need(value, message):
    if not value:
        raise ValueError(message)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', type=Path, required=True)
    p.add_argument('--audit-root', type=Path, required=True)
    a = p.parse_args()
    root, audit_root = a.project_root.resolve(), a.audit_root.resolve()
    need(audit_root.is_relative_to(root), 'Project-local independent actual audit')
    order = runpy.run_path(str(root / MODEL / 'order.py'))
    languages = {}
    for mode in ('c', 'cpp'):
        folder = root / MODEL / ('build/prototype-' + mode)
        receipt = folder / 'order-receipt.json'
        current = order['replay'](root, receipt)
        audit_path = audit_root / ('build/order-prototype-' + mode) / 'audit.json'
        audit = json.loads(audit_path.read_bytes())
        need(audit['passed'] and audit['independent_native']['passed'], 'Independent actual audit passed')
        for key, count in [('actual_ELF_controls', 18), ('path_controls', 5), ('receipt_controls', 3)]:
            need(len(audit[key]) == count and all(row.get('rejected', row.get('rejected_before_write'))
                                               for row in audit[key]), 'Actual rejected control inventory')
        need(audit['tool_sha256'] == current['tool_sha256']
             and audit['policy_sha256'] == current['policy_sha256']
             and audit['input_sha256'] == current['input']['sha256']
             and audit['output_sha256'] == current['output']['sha256'],
             'Independent actual control audit bound to replayed exact objects/tool/policy')
        archive = HERE / ('audit-' + mode + '.json')
        with archive.open('xb') as out:
            out.write(audit_path.read_bytes())
        languages[mode] = dict(receipt=current, independent_audit=archive.name,
                               independent_audit_sha256=sha(archive),
                               actual_ELF_controls=18, path_controls=5, receipt_controls=3)
    value = dict(schema='TSL9-page-reply-ABI-order-archived-verification-v1', passed=True,
                 languages=languages, compiler_source_provenance_verified_here=False,
                 original_BIN_read_for_generation=False, target_execution=False,
                 ISA_emulation=False, hardware=False, OTA_ready=False)
    with (HERE / 'verification.json').open('xb') as out:
        out.write((json.dumps(value, indent=2) + '\n').encode())
    print(json.dumps(dict(passed=True, languages=list(languages), controls_per_language=26,
                         actual_ELF_replays=2, target_execution=False)))


if __name__ == '__main__':
    main()
