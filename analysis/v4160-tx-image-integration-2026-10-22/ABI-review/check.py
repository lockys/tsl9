#!/usr/bin/env python3
"""Read-only source/metadata validation; never open a generated build or firmware."""
import argparse
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value,message):
    if not value:
        raise ValueError(message)


def dependency(root,name):
    path=root/name
    if not path.exists() and name.startswith('apk-analysis/tsl9-'):
        path=root/'analysis'/name[len('apk-analysis/tsl9-'):]
    return path


def check(root):
    seal=json.loads((HERE/'seal.json').read_bytes())
    require(seal['schema']=='TSL9-TX-full-image-independent-ABI-seal-v1','Known sealed metadata schema')
    require(not seal['generated_build_artifacts_included'],'Metadata bundle excludes build artifacts')
    for item in seal['files']:
        path=(HERE/item['path']).resolve()
        require(path.is_relative_to(HERE) and 'build' not in path.relative_to(HERE).parts,
                'Sealed member inside source/metadata bundle')
        require(path.stat().st_size==item['bytes'] and sha(path)==item['sha256'],
                'Unchanged source/metadata member '+item['path'])
    dependencies=json.loads((HERE/'dependency-pins.json').read_bytes())
    for item in dependencies:
        path=dependency(root,item['path'])
        require(path.is_file() and sha(path)==item['sha256'],'Pinned read-only helper '+item['path'])
    require((HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes(),
            'Default README is the full Traditional Chinese text')
    return dict(passed=True,mode='metadata-only',source_metadata_members=len(seal['files']),
                pinned_helper_sources=len(dependencies),actual_build_artifact_replay=False,
                actual_original_firmware_read=False,static_full_image_contract_passed_this_run=False,
                original_full_ABI_admitted=False,hardware_OTA_proved=False)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=HERE.parents[2])
    a=p.parse_args();print(json.dumps(check(a.project_root.resolve())))
