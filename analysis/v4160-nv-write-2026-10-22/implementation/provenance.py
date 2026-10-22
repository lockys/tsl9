#!/usr/bin/env python3
"""Read original firmware and re-decode six bounded source groups only."""
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
    dp=locate(root,proof['decoder']['path'])
    if H(dp)!=proof['decoder']['sha256']:raise ValueError('Sealed binding decoder identity')
    _,decode,_,_=runpy.run_path(str(dp))['context'](root);raw=firmware.read_bytes();total=0;rows_count=0
    for name,b in proof['bounds'].items():
        chunk=raw[b['start']-proof['firmware_origin']:b['end_exclusive']-proof['firmware_origin']]
        if hashlib.sha256(chunk).hexdigest()!=b['sha256']:raise ValueError('Original group '+name)
        rows=[];offset=0
        while offset<len(chunk):
            row=decode(chunk[offset:],b['start']+offset);rows.append(row);offset+=row['bytes']
        if rows!=proof['groups'][name]:raise ValueError('Every raw operand '+name)
        if name=='write_cb' and chunk!=(case/'original-write-197be.bin').read_bytes():raise ValueError('Write evidence slice')
        if name=='timer' and chunk!=(case/'original-timer-19764.bin').read_bytes():raise ValueError('Timer evidence slice')
        total+=len(chunk);rows_count+=len(rows)
    if (total,rows_count)!=(294,115):raise ValueError('Bounded source extent')
    return dict(passed=True,actual_original_firmware_read=True,groups=6,bytes=total,rows=rows_count,native_execution=False,ISA_emulation=False)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--firmware',required=True,type=Path);a=p.parse_args();print(json.dumps(actual(a.project_root.resolve(),a.firmware.resolve())))
if __name__=='__main__':main()
