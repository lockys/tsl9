#!/usr/bin/env python3
"""Metadata-only sealed bundle check. Does not open a generated native archive."""
import argparse
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def check(root):
    root=Path(root).resolve();seal=json.loads((HERE/'seal.json').read_bytes())
    if seal['schema']!='TSL9-callback-call-frontiers-native-seal-v1':raise ValueError('Seal schema')
    for item in seal['files']:
        p=(HERE/item['path']).resolve()
        if not p.is_relative_to(HERE) or not p.is_file():raise ValueError('Bounded sealed member')
        data=p.read_bytes()
        if len(data)!=item['bytes'] or hashlib.sha256(data).hexdigest()!=item['sha256']:
            raise ValueError('Sealed source/metadata member mismatch '+item['path'])
    if (HERE/'README.md').read_bytes()!=(HERE/'readme.zh-TW.md').read_bytes():
        raise ValueError('Default README equals full Traditional Chinese document')
    return dict(passed=True,metadata_only=True,sealed_members=len(seal['files']),
                actual_native_artifacts_read=False,actual_call_frontiers_checked=False,
                original_firmware_read=False,previous_recorded_semantic_matches=15,
                full_original_ABI_admitted=False,hardware_OTA_proved=False)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path)
    a=p.parse_args();print(json.dumps(check(a.project_root)))
