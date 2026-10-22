#!/usr/bin/env python3
"""Default source/metadata checks; never claim an actual build replay."""
import argparse
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def need(value,message):
    if not value:raise ValueError(message)


def check(root):
    seal=json.loads((HERE/'seal.json').read_bytes())
    need(seal['schema']=='TSL9-callback-independent-ABI-metadata-seal-v1','Known independent seal schema')
    for item in seal['files']:
        path=(HERE/item['path']).resolve()
        need(path.is_relative_to(HERE) and 'build' not in path.relative_to(HERE).parts and
             path.stat().st_size==item['bytes'] and sha(path)==item['sha256'],'Exact source/metadata member')
    for name,pin in json.loads((HERE/'core-pins.json').read_bytes()).items():
        need(sha(root/'experiments/tsl9-v4160-event-callback/src'/name)==pin,'Frozen current callback source '+name)
    need(sha(root/'experiments/tsl9-v4160-flash-register-prefix/verify_host.py')==
         'f1982360434f89dcf661e8b143ae5e9d4822c76d9837ec6bf1c2e94c639713eb','Immutable HOST launch machine guard')
    need((HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes(),'Default full Traditional Chinese')
    return dict(passed=True,mode='metadata-only',members=len(seal['files']),
                actual_original_firmware_read=False,actual_host_artifacts_replayed=False,
                actual_native_artifacts_read=False,original_full_ABI_admitted=False,
                placement_admitted=False,hardware_OTA_proved=False)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=HERE.parents[2])
    a=p.parse_args();print(json.dumps(check(a.project_root.resolve())))
