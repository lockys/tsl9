#!/usr/bin/env python3
"""Read original FW and statically re-decode the retained30B; never execute."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys
sys.dont_write_bytecode=True
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def locate(root,name):
    p=root/name
    if p.is_file():return p
    if name.startswith('apk-analysis/tsl9-'):return root/('analysis/'+name[len('apk-analysis/tsl9-'):])
    return p
def actual(root,firmware):
    case=Path(__file__).resolve().parent;proof=json.loads((case/'source-proof.json').read_bytes())
    if H(firmware)!=proof['firmware_sha256'] or firmware.stat().st_size!=proof['firmware_bytes']:raise ValueError('Original firmware identity')
    raw=firmware.read_bytes()[proof['file_offset']:proof['file_offset']+proof['bytes']]
    if raw!=(case/'original-1979a-197b8.bin').read_bytes() or hashlib.sha256(raw).hexdigest()!=proof['raw_sha256']:raise ValueError('Actual source30B')
    path=locate(root,proof['decoder']['path'])
    if H(path)!=proof['decoder']['sha256']:raise ValueError('Retained finite decoder identity')
    decode=runpy.run_path(str(path))['decoder'](root);rows=[];offset=0
    while offset<len(raw):
        row=decode(raw[offset:],proof['range'][0]+offset);rows.append(row);offset+=row['bytes']
    if rows!=proof['rows'] or len(rows)!=13 or offset!=30:raise ValueError('Complete original instruction fields')
    return dict(passed=True,actual_original_firmware_read=True,bytes=30,rows=13,raw_sha256=proof['raw_sha256'],original_C_prototype_proved=False,target_execution=False,ISA_emulation=False)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--firmware',required=True,type=Path);a=p.parse_args();print(json.dumps(actual(a.project_root.resolve(),a.firmware.resolve())))
if __name__=='__main__':main()
