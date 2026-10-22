#!/usr/bin/env python3
"""Metadata closure for ADC C/C++ and source dependencies; never execute targets."""
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
    observation = json.loads((HERE / 'instruction-reference/observation.json').read_bytes())
    for name, row in observation['excerpts'].items():
        path = HERE / 'instruction-reference' / name
        if sha(path) != row['sha256'] or path.stat().st_size != row['bytes']:
            raise ValueError('Actual captured ISA excerpt: ' + name)
    print(json.dumps(dict(passed=True, metadata_only=True, sealed_members=len(seal['members']),
                          versioned_dependencies=len(seal['external_inputs']),
                          actual_firmware_or_objects_read=False, compiler_invoked=False,
                          HOST_or_native_adapter_executed=False, source_ADC_functions=8,
                          original_full_ABI_proved=False, original_extent_ownership_proved=False,
                          new_BIN=False, native_candidate_promoted=False,
                          installed_chip_identity_proved=False, physical_OTA_proved=False)))


if __name__ == '__main__':
    main()
