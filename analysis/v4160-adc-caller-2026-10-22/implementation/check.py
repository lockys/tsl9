#!/usr/bin/env python3
"""Source metadata by default; actual native readback only on explicit receipts."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy
import sys
sys.dont_write_bytecode=True
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def locate(root,name):
    p=root/name
    if p.is_file():return p
    if name.startswith('apk-analysis/tsl9-'):return root/('analysis/'+name[len('apk-analysis/tsl9-'):])
    return p
def whitespace(path):
    data=path.read_bytes()
    if b'\r' in data or not data.endswith(b'\n') or data.endswith(b'\n\n'):raise ValueError('LF/single EOF '+str(path))
    for line in data.splitlines():
        if re.search(rb'[ \t]+$',line) or re.match(rb'^[ \t]* +\t',line):raise ValueError('Git-style whitespace '+str(path))
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--receipt',action='append',default=[],type=Path);a=p.parse_args();root=a.project_root.resolve();case=Path(__file__).resolve().parent;s=json.loads((case/'seal.json').read_bytes())
    for group in ('members','model_members','external_pins'):
        for item in s[group]:
            f=locate(root,item['path'])
            if f.stat().st_size!=item['bytes'] or H(f)!=item['sha256']:raise ValueError('Pinned '+item['path'])
            if group!='external_pins':whitespace(f)
    whitespace(case/'seal.json')
    for folder in (case,root/'experiments/tsl9-adc-caller-bank'):
        if (folder/'README.md').read_bytes()!=(folder/'readme.zh-TW.md').read_bytes():raise ValueError('Traditional Chinese default identity')
    module=runpy.run_path(str(case/'probe.py'));results=[module['replay'](root,r) for r in a.receipt]
    print(json.dumps(dict(passed=True,metadata_only=not a.receipt,actual_native_artifacts_read=bool(a.receipt),results=results,strict_LF_single_EOF_Git_style_whitespace=True,full_original_callee_ABI_proved=False,producer_specific_caller_normal_projection_proved=False,installed_provider_proved=False,placement_proved=False,HOST_matrix_rerun=False,native_execution=False,ISA_emulation=False,BIN_exported=False,hardware_OTA_proved=False)))
if __name__=='__main__':main()
