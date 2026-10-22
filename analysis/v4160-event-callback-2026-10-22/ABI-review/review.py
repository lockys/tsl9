#!/usr/bin/env python3
"""Explicit original-source, conditional-HOST and actual-native evidence bundle."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(root,firmware,host_receipt,native_folder):
    source=runpy.run_path(str(HERE/'source.py'));host=runpy.run_path(str(HERE/'run-host.py'))
    native=runpy.run_path(str(HERE/'native.py'))
    return dict(schema='TSL9-callback-independent-layered-review-v1',
                actual_original_firmware_read=True,actual_host_artifacts_replayed=True,
                actual_native_artifacts_read=True,source=source['inspect'](firmware),
                HOST=host['replay'](root,host_receipt),native=native['inspect'](root,native_folder),
                host_receipt=host_receipt.relative_to(root).as_posix(),
                host_receipt_sha256=sha(host_receipt),native_folder=native_folder.relative_to(root).as_posix(),
                review_source_sha256={name:sha(HERE/name) for name in
                                      ('review.py','source.py','run-host.py','native.py','independent_host.c')},
                complete_physical_GPR_residues_proved=False,restored_return_target_executed=False,
                original_full_ABI_admitted=False,placement_admitted=False,
                target_execution=False,ISA_emulation=False,hardware_OTA_proved=False)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True)
    p.add_argument('--firmware',type=Path,required=True);p.add_argument('--host-receipt',type=Path)
    p.add_argument('--native-folder',type=Path);p.add_argument('--receipt',type=Path)
    p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:
        if a.host_receipt or a.native_folder or a.receipt:raise ValueError('Readonly replay has no new inputs/output')
        prior=json.loads(a.replay.read_bytes())
        result=inspect(root,a.firmware.resolve(),root/prior['host_receipt'],root/prior['native_folder'])
        if result!=prior:raise ValueError('Exact layered actual artifact replay')
    else:
        if not a.host_receipt or not a.native_folder or not a.receipt or a.receipt.exists():
            raise ValueError('Explicit actual HOST/native artifacts and create-only receipt')
        result=inspect(root,a.firmware.resolve(),a.host_receipt.resolve(),a.native_folder.resolve())
        a.receipt.parent.mkdir(parents=True,exist_ok=True)
        a.receipt.write_bytes((json.dumps(result,indent=2)+'\n').encode('utf8'))
    print(json.dumps(dict(passed=True,actual_host_artifacts_replayed=True,actual_native_artifacts_read=True,
                         conditional_HOST_only=True,native_bytes=result['native']['facts']['allocated_bytes'],
                         original_full_ABI_admitted=False,placement_admitted=False,hardware_OTA_proved=False)))
