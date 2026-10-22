#!/usr/bin/env python3
"""Read-only callback-frontier metadata closure; no target or compiler invocation."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    s = json.loads((HERE / 'parent-seal.json').read_bytes())
    for name, pin in s['members'].items():
        p = (HERE / name).resolve()
        if not p.is_relative_to(HERE) or sha(p) != pin:
            raise ValueError('Callback frontier member ' + name)
    for name, pin in s['external_inputs'].items():
        p = ROOT / name
        if name.startswith('analysis/') and not p.is_file():
            p = ROOT / ('apk-analysis/tsl9-' + name.removeprefix('analysis/'))
        if not p.resolve().is_relative_to(ROOT) or sha(p) != pin:
            raise ValueError('Versioned dependency ' + name)
    if (HERE / 'README.md').read_bytes() != (HERE / 'readme.zh-TW.md').read_bytes():
        raise ValueError('Full Traditional Chinese default')
    print(json.dumps(dict(passed=True, metadata_only=True, sealed_members=len(s['members']),
                          versioned_dependencies=len(s['external_inputs']),
                          actual_firmware_or_native_artifacts_read=False,
                          compiler_invoked=False, target_execution=False,
                          full_original_ABI_proved=False, installed_ROM_proved=False,
                          Flash_NV_ownership_proved=False, hardware_OTA_proved=False,
                          new_BIN=False, rebuilt_flashable_BIN=False)))


if __name__ == '__main__':
    main()
