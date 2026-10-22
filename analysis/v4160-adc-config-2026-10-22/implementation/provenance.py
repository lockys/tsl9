#!/usr/bin/env python3
"""Read the supplied original firmware and re-decode only the retained88B."""
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
    if raw!=(case/'original-1892e-18986.bin').read_bytes() or hashlib.sha256(raw).hexdigest()!=proof['raw_sha256']:raise ValueError('Actual source88B')
    decoder_path=locate(root,proof['decoder']['path'])
    if H(decoder_path)!=proof['decoder']['sha256']:raise ValueError('Retained decoder identity')
    decode=runpy.run_path(str(decoder_path))['decoder'](root);rows=[];offset=0
    while offset<len(raw):
        row=decode(raw[offset:],proof['range'][0]+offset);rows.append(row);offset+=row['bytes']
    if rows!=proof['rows'] or len(rows)!=37 or offset!=88:raise ValueError('Actual complete raw operand replay')
    return dict(passed=True,actual_original_firmware_read=True,bytes=88,rows=37,effects=sum(r['memory_width'] is not None for r in rows),firmware_sha256=H(firmware),raw_sha256=proof['raw_sha256'],target_execution=False,ISA_emulation=False)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--firmware',required=True,type=Path);a=p.parse_args();print(json.dumps(actual(a.project_root.resolve(),a.firmware.resolve())))
if __name__=='__main__':main()
