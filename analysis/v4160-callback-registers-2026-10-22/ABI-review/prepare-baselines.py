#!/usr/bin/env python3
"""Optional historical artifact read; retained rows/hashes are verification only."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(root):
    f=runpy.run_path(str(HERE/'fields.py'));ctx=f['context'](root);result={}
    for name,folder in (
        ('sealed658',root/'experiments/tsl9-v4160-event-callback/build/formal-native/c'),
        ('fixed656',root/'experiments/tsl9-v4160-callback-registers/build/first-profile/c')):
        e=ctx['ELF'](folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf');section=e.byname['.text']
        result[name]=dict(verification_only=True,ELF_sha256=sha(folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf'),
                          bytes=section['size'],code_sha256=hashlib.sha256(e.data(section)).hexdigest(),
                          rows=f['rows'](e.data(section),section['address'],ctx))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    if a.output.exists():raise ValueError('Create-only verification baseline')
    a.output.write_bytes((json.dumps(prepare(a.project_root.resolve()),indent=2)+'\n').encode('utf8'))
