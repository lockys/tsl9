#!/usr/bin/env python3
"""Metadata-only default; explicit receipts inspect the actual native files."""
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
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--receipt',action='append',default=[],type=Path);a=p.parse_args();root=a.project_root.resolve();case=Path(__file__).resolve().parent;s=json.loads((case/'seal.json').read_bytes())
    for group in ('members','model_members','external_pins'):
        for item in s[group]:
            path=locate(root,item['path'])
            if path.stat().st_size!=item['bytes'] or H(path)!=item['sha256']:raise ValueError('Pinned '+item['path'])
    module=runpy.run_path(str(case/'probe.py'));results=[module['replay'](root,r) for r in a.receipt]
    print(json.dumps(dict(passed=True,metadata_only=not a.receipt,actual_native_artifacts_read=bool(a.receipt),results=results,original_full_register_ABI_proved=False,installed_provider_proved=False,HOST_adapter_execution=False,target_execution=False,ISA_emulation=False,linked=False,BIN_exported=False,hardware_OTA_proved=False)))
if __name__=='__main__':main()
