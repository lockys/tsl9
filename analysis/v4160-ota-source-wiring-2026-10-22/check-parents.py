#!/usr/bin/env python3
"""Read-only closure of this milestone's documentation and versioned evidence."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def need(v, message):
    if not v:
        raise ValueError(message)


def locate(name):
    path = ROOT / name
    if name.startswith('analysis/') and not path.exists():
        path = ROOT / ('apk-analysis/tsl9-' + name.removeprefix('analysis/'))
    need(path.resolve().is_relative_to(ROOT), 'Contained versioned dependency')
    return path


def main():
    seal = json.loads((HERE / 'parent-seal.json').read_bytes())
    for name, pin in seal['members'].items():
        p = HERE / name
        need(p.resolve().is_relative_to(HERE) and sha(p) == pin, 'Parent member: ' + name)
    for name, pin in seal['external_inputs'].items():
        need(sha(locate(name)) == pin, 'Versioned dependency: ' + name)
    need((HERE / 'README.md').read_bytes() == (HERE / 'readme.zh-TW.md').read_bytes(), 'Full Traditional Chinese default')
    boundary = json.loads((HERE / 'original-ROM-boundary.json').read_bytes())
    need(boundary['source_pc'] == 0x18730 and boundary['raw_hex'] == '6f70120d'
         and boundary['rd'] == 0 and boundary['numerical_target'] == 0x40000
         and boundary['original_relocation']['true_UND']
         and not boundary['ROM_implementation_provider'], 'Numerical boundary and true-provider distinction')
    print(json.dumps(dict(passed=True, metadata_only=True, sealed_parent_members=len(seal['members']),
                          versioned_dependencies=len(seal['external_inputs']), actual_image_artifacts_read=False,
                          actual_original_firmware_read=False, HOST_suites_rerun=False, ROM_provider=False,
                          numerical_address_witness_only=True, original_ABI_admitted=False,
                          physical_Flash_NV_ownership_proved=False, hardware_OTA_proved=False,
                          compiler_or_target_execution=False)))


if __name__ == '__main__':
    main()
