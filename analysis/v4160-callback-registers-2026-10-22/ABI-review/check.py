#!/usr/bin/env python3
"""Source/metadata-only default; no archived native-build requirement."""
import argparse
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def need(value,message):
    if not value:raise ValueError(message)


def check(root):
    seal=json.loads((HERE/'seal.json').read_bytes())
    need(seal['schema']=='TSL9-callback-register-independent-metadata-seal-v1','Known seal schema')
    for item in seal['files']:
        path=(HERE/item['path']).resolve()
        need(path.is_relative_to(HERE) and 'build' not in path.relative_to(HERE).parts and
             path.stat().st_size==item['bytes'] and sha(path)==item['sha256'],'Exact source/metadata member')
    for item in json.loads((HERE/'source-pins.json').read_bytes()):
        path=root/item['path']
        if not path.exists() and item['path'].startswith('apk-analysis/tsl9-'):
            path=root/'analysis'/item['path'][len('apk-analysis/tsl9-'):]
        need(sha(path)==item['sha256'],'Unchanged reviewed source/profile input')
    need((HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes(),'Full Traditional Chinese default')
    return dict(passed=True,mode='metadata-only',members=len(seal['files']),
                actual_native_artifacts_read=False,actual_ordered_artifacts_replayed=False,
                HOST_suite_rerun=False,whole632_storage_covered=False,
                original_full_ABI_admitted=False,placement_admitted=False,hardware_OTA_proved=False)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=HERE.parents[2])
    a=p.parse_args();print(json.dumps(check(a.project_root.resolve())))
