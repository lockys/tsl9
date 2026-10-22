#!/usr/bin/env python3
"""Source/metadata by default; explicitly selected HOST/native archive replay."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys
sys.dont_write_bytecode=True
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def locate(root,path):
    p=root/path
    if p.is_file():return p
    if path.startswith('apk-analysis/tsl9-'):return root/('analysis/'+path[len('apk-analysis/tsl9-'):])
    return p
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--host-receipt',action='append',default=[],type=Path);p.add_argument('--native-receipt',action='append',default=[],type=Path);a=p.parse_args();root=a.project_root.resolve();case=Path(__file__).resolve().parent;s=json.loads((case/'seal.json').read_bytes())
    for group in ('members','model_members','external_pins'):
        for item in s[group]:need(H(locate(root,item['path']))==item['sha256'],'Pinned '+item['path'])
    for name,item in s['review_seals'].items():need(H(locate(root,item['path']))==item['sha256'],'Independent '+name)
    host=[];native=[]
    if a.host_receipt:
        module=runpy.run_path(str(root/'experiments/tsl9-resident-memory-leaves/verify_host.py'))
        host=[module['replay'](root,r) for r in a.host_receipt]
    if a.native_receipt:
        module=runpy.run_path(str(case/'probe.py'));native=[module['replay'](root,r) for r in a.native_receipt]
    print(json.dumps(dict(passed=True,metadata_only=not(a.host_receipt or a.native_receipt),actual_host_archives_read=bool(a.host_receipt),actual_native_artifacts_read=bool(a.native_receipt),host=host,native=native,installed_identity_proved=False,native_candidate_ABI_proved=False,original_or_candidate_execution=False,ISA_emulation=False,hardware_OTA_proved=False,linked=False,BIN_exported=False)))
if __name__=='__main__':main()
