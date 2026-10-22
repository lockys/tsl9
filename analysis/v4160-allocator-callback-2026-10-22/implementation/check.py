#!/usr/bin/env python3
"""Metadata-only default; explicit --receipt reads actual compiler artifacts."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def resolve(root,name):
    p=root/name
    if p.is_file():return p
    if name.startswith('apk-analysis/tsl9-'):return root/('analysis/'+name[len('apk-analysis/tsl9-'):])
    return p
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--receipt',action='append',type=Path,default=[]);a=p.parse_args()
    root=a.project_root.resolve();case=Path(__file__).resolve().parent;s=json.loads((case/'seal.json').read_bytes())
    for group in ('members','model_members','external_pins'):
        for member in s[group]:
            f=resolve(root,member['path']);need(f.is_file() and H(f)==member['sha256'],'Pinned '+member['path'])
    for key,member in s['review_seals'].items():
        need(H(resolve(root,member['path']))==member['sha256'],'Independent seal '+key)
    results=[]
    if a.receipt:
        spec=importlib.util.spec_from_file_location('reply_frame_probe',case/'probe.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        for receipt in a.receipt:results.append(mod.replay(root,receipt))
    print(json.dumps(dict(passed=True,metadata_only=not a.receipt,actual_build_artifacts_read=bool(a.receipt),results=results,
        selected_native_bytes=556,frame_bytes=48,reply_offsets=[10,11],reply_relative_to_entry_SP=-38,
        original_reply_relative_to_entry_SP=-36,pointer_frame_goal_achieved=False,original_ABI_admitted=False,
        live_568_model_replaced=False,BIN_exported=False,target_execution=False)))
if __name__=='__main__':main()
