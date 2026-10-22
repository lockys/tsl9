#!/usr/bin/env python3
"""Default source/metadata validation, never a generated-archive replay."""
import argparse
import hashlib
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def need(value,message):
    if not value:raise ValueError(message)


def check(root):
    root=Path(root).resolve();seal=json.loads((HERE/'seal.json').read_bytes())
    need(seal['schema']=='TSL9-OTA-handler-independent-ABI-HOST-seal-v1','Exact source/metadata seal schema')
    for item in seal['files']:
        path=(HERE/item['path']).resolve()
        need(path.is_relative_to(HERE) and path.is_file() and path.stat().st_size==item['bytes']
             and sha(path)==item['sha256'],'Sealed source/metadata member '+item['path'])
    need((HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes(),'Full Traditional Chinese default README')
    for name,pin in json.loads((HERE/'core-pins.json').read_bytes()).items():
        need(sha(root/'experiments/tsl9-v4160-ota-handler/src'/name)==pin,'Current frozen shared source '+name)
    return dict(passed=True,metadata_only=True,sealed_members=len(seal['files']),current_shared_sources_checked=4,
                actual_host_artifacts_replayed=False,actual_native_artifacts_read=False,
                original_firmware_read=False,full_original_ABI_admitted=False,hardware_OTA_proved=False)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path)
    a=p.parse_args();print(json.dumps(check(a.project_root)))
