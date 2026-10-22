#!/usr/bin/env python3
"""Check component metadata, or explicitly reread an existing link receipt."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', required=True, type=Path)
    p.add_argument('--component-receipt', type=Path)
    a = p.parse_args(); root = a.project_root.resolve()
    seal = json.loads((HERE / 'seal.json').read_bytes())
    for name, pin in seal['members'].items():
        path = (HERE / name).resolve()
        if not path.is_relative_to(HERE) or sha(path) != pin:
            raise ValueError('Component metadata member ' + name)
    for name, pin in seal['external_inputs'].items():
        path = root / name
        if name.startswith('analysis/') and not path.is_file():
            path = root / ('apk-analysis/tsl9-' + name.removeprefix('analysis/'))
        if sha(path) != pin:
            raise ValueError('Versioned component dependency ' + name)
    if (HERE / 'README.md').read_bytes() != (HERE / 'readme.zh-TW.md').read_bytes():
        raise ValueError('Traditional Chinese default')
    result = runpy.run_path(str(HERE / 'probe.py'))['replay'](root, a.component_receipt.resolve()) if a.component_receipt else None
    print(json.dumps(dict(passed=True, metadata_only=result is None,
                          actual_artifacts_read=result is not None, result=result,
                          compiler_or_linker_invoked=False, target_execution=False,
                          component_VMA_is_physical=False, full_original_ABI_proved=False,
                          hardware_OTA_proved=False, BIN_generated=False, rebuilt_flashable_BIN=False)))


if __name__ == '__main__':
    main()
