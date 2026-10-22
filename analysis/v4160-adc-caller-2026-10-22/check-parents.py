#!/usr/bin/env python3
"""Read-only metadata closure; actual artifact checks are explicit separate modes."""
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
            raise ValueError('Parent metadata member: ' + name)
    for name, pin in seal['external_inputs'].items():
        path = ROOT / name
        if name.startswith('analysis/') and not path.is_file():
            path = ROOT / ('apk-analysis/tsl9-' + name.removeprefix('analysis/'))
        if not path.resolve().is_relative_to(ROOT) or sha(path) != pin:
            raise ValueError('Versioned dependency: ' + name)
    if (HERE / 'README.md').read_bytes() != (HERE / 'readme.zh-TW.md').read_bytes():
        raise ValueError('Full Traditional Chinese default')
    print(json.dumps(dict(passed=True, metadata_only=True,
                          sealed_members=len(seal['members']),
                          versioned_dependencies=len(seal['external_inputs']),
                          actual_ELF_or_firmware_read=False,
                          compiler_or_linker_invoked=False,
                          target_or_HOST_execution=False,
                          full_original_callee_ABI_proved=False,
                          full_image_provenance_proved=False,
                          installed_ROM_proved=False,
                          Flash_NV_ownership_proved=False,
                          hardware_OTA_proved=False,
                          rebuilt_flashable_BIN=False)))


if __name__ == '__main__':
    main()
