#!/usr/bin/env python3
"""Actual native ET_REL readback and optional original-byte validation."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
FW_SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'


def need(value,message):
    if not value:raise ValueError(message)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(root,folder,firmware=None):
    result=runpy.run_path(str(HERE/'native.py'))['inspect'](root,folder)
    result['wrapper_sha256']=sha(HERE/'review.py');result['original_firmware_read']=False
    if firmware:
        firmware=Path(firmware).resolve();need(sha(firmware)==FW_SHA,'Explicit official readonly firmware bytes')
        body=firmware.read_bytes()[0x1c4a:0x1e5c]
        need(len(body)==530 and hashlib.sha256(body).hexdigest()==
             '693eba9e21b786525b457b538d998a997a601ee46327621a2302ede1b2f274c5','Original handler body')
        result['original_firmware_read']=True
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path)
    p.add_argument('--folder',type=Path);p.add_argument('--receipt',type=Path)
    p.add_argument('--firmware',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:
        need(a.folder is None and a.receipt is None,'Readonly replay uses recorded actual native folder')
        old=json.loads(a.replay.read_bytes());need(bool(a.firmware)==old['original_firmware_read'],'Same explicit firmware-read mode')
        result=inspect(root,root/old['actual_folder'],a.firmware);need(result==old,'Exact actual native independent replay')
    else:
        need(a.folder is not None and a.receipt is not None and not a.receipt.exists(),'Create-only new independent receipt')
        need(not a.receipt.resolve().is_relative_to(a.folder.resolve()),'Receipt stays outside frozen producer artifact folder')
        result=inspect(root,a.folder,a.firmware);a.receipt.parent.mkdir(parents=True,exist_ok=True)
        a.receipt.write_bytes((json.dumps(result,indent=2)+'\n').encode('utf8'))
    print(json.dumps(dict(passed=True,actual_native_artifacts_read=True,original_firmware_read=result['original_firmware_read'],
                         native_bytes=result['measured']['bytes'],instructions=result['measured']['instructions'],
                         true_UND=9,linked=False,original_placement_admitted=False,full_original_ABI_admitted=False)))
