#!/usr/bin/env python3
"""Metadata-only: never read firmware or generated build archives by default."""
import argparse
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def H(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve(root,name):
    direct=root/name
    if direct.is_file():
        return direct
    prefix='apk-analysis/tsl9-'
    if name.startswith(prefix):
        return root/('analysis/'+name[len(prefix):])
    return direct


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--project-root',type=Path,required=True)
    args=parser.parse_args();root=args.project_root.resolve()
    seal=json.loads((HERE/'seal.json').read_bytes())
    for item in seal['files']:
        path=HERE/item['path']
        if not path.is_file() or path.stat().st_size!=item['bytes'] or H(path)!=item['sha256']:
            raise ValueError('Sealed source/metadata member changed: '+item['path'])
    summary=json.loads((HERE/'summary.json').read_bytes())
    for name,expected in summary['external_source_pins'].items():
        if H(resolve(root,name))!=expected:
            raise ValueError('External source dependency changed: '+name)
    if summary['original_full_ABI_admitted'] is not False or summary['whole_image_integrated'] is not False:
        raise ValueError('Partial static admission boundaries must remain explicit')
    print(json.dumps(dict(metadata_checked=True,actual_build_artifact_replay=False,
                         firmware_read=False,original_full_ABI_admitted=False,
                         whole_image_integrated=False,sealed_members=len(seal['files']))))


if __name__=='__main__':
    main()
