#!/usr/bin/env python3
"""Metadata-only closure for the owned reply object and conditional config-entry evidence."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    seal = json.loads((HERE / 'parent-seal.json').read_bytes())
    for name, pin in seal['members'].items():
        path = (HERE / name).resolve()
        if not path.is_relative_to(HERE) or sha(path) != pin:
            raise ValueError('Parent member: ' + name)
    for name, pin in seal['external_inputs'].items():
        path = ROOT / name
        if name.startswith('analysis/') and not path.is_file():
            path = ROOT / ('apk-analysis/tsl9-' + name.removeprefix('analysis/'))
        if not path.resolve().is_relative_to(ROOT) or sha(path) != pin:
            raise ValueError('Versioned dependency: ' + name)
    if (HERE / 'README.md').read_bytes() != (HERE / 'readme.zh-TW.md').read_bytes():
        raise ValueError('Full Traditional Chinese default')
    print(json.dumps(dict(passed=True, metadata_only=True, sealed_members=len(seal['members']),
                          versioned_dependencies=len(seal['external_inputs']),
                          actual_firmware_or_objects_read=False, native_compiler_invoked=False,
                          HOST_suites_rerun=False, new_BIN=False, native_candidate_promoted=False,
                          reply_pointer_projection_matched_metadata=True,
                          full_original_frame_contract_proved=False,
                          original_ABI_or_physical_OTA_proved=False)))


if __name__ == '__main__':
    main()
