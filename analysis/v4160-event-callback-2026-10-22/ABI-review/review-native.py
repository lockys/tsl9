#!/usr/bin/env python3
"""Explicit actual-native review wrapper; all admission flags remain false."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(root,folder):
    if not folder.is_relative_to(root):raise ValueError('Actual folder inside explicit project root')
    source=HERE/'native.py'
    if sha(source)!='ec333f3d28653c6e625a8c67e95cb1dd3a9621bb16ccfa2862ce47e7fb30abf7':
        raise ValueError('Frozen independent pure native diagnostic')
    result=runpy.run_path(str(source))['inspect'](root,folder)
    result['actual_folder']=folder.relative_to(root).as_posix()
    result['actual_artifacts']={name:dict(bytes=(folder/name).stat().st_size,sha256=sha(folder/name))
                               for name in ('callback.o','callback.ll','COMPONENT-ONLY-NOT-FIRMWARE.elf',
                                            'complete-static-disassembly.log')}
    producer=folder/'verification.json'
    result['producer_receipt_sha256']=sha(producer) if producer.exists() else None
    result['review_source_sha256']=sha(source)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path)
    p.add_argument('--folder',type=Path);p.add_argument('--receipt',type=Path)
    p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:
        if a.folder or a.receipt:raise ValueError('Readonly replay has no new folder/output')
        prior=json.loads(a.replay.read_bytes());result=inspect(root,(root/prior['actual_folder']).resolve())
        if result!=prior:raise ValueError('Exact actual-native independent receipt replay')
    else:
        if not a.folder or not a.receipt or a.receipt.exists():
            raise ValueError('Actual folder and create-only independent receipt')
        result=inspect(root,a.folder.resolve());a.receipt.parent.mkdir(parents=True,exist_ok=True)
        a.receipt.write_bytes((json.dumps(result,indent=2)+'\n').encode('utf8'))
    print(json.dumps(dict(passed=True,actual_native_artifacts_read=True,
                         actual_native_artifacts_replayed=True,
                         native_bytes=result['facts']['allocated_bytes'],
                         fits_original_extent=result['facts']['fits_original_extent'],
                         original_full_ABI_admitted=False,placement_admitted=False,hardware_OTA_proved=False)))
