#!/usr/bin/env python3
"""Verify sealed integration metadata or explicitly replay an existing artifact."""
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
    p.add_argument('--project-root',required=True,type=Path)
    p.add_argument('--integration-receipt',type=Path)
    a=p.parse_args();seal=json.loads((HERE/'seal.json').read_bytes())
    for name,pin in seal['members'].items():
        path=(HERE/name).resolve()
        if not path.is_relative_to(HERE) or sha(path)!=pin:
            raise ValueError('Integration source member: '+name)
    for name,pin in seal['external_inputs'].items():
        path=a.project_root/name
        if name.startswith('analysis/') and not path.is_file():
            path=a.project_root/('apk-analysis/tsl9-'+name.removeprefix('analysis/'))
        if sha(path)!=pin:
            raise ValueError('Integration dependency: '+name)
    if (HERE/'README.md').read_bytes()!=(HERE/'readme.zh-TW.md').read_bytes():
        raise ValueError('Full Traditional Chinese default')
    result=runpy.run_path(str(HERE/'probe.py'))['replay'](a.project_root.resolve(),a.integration_receipt.resolve()) if a.integration_receipt else None
    print(json.dumps(dict(passed=True,metadata_only=result is None,actual_artifacts_read=result is not None,
                          result=result,compiler_or_linker_invoked=False,target_execution=False,
                          hardware_OTA_proved=False,rebuilt_flashable_BIN=False)))


if __name__=='__main__':
    main()
