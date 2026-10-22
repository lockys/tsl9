#!/usr/bin/env python3
"""Sealed metadata/current-source verification; no actual build archive needed."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(root):
    seal=json.loads((HERE/'seal.json').read_bytes())
    for name,pin in seal['members'].items():need(sha(HERE/name)==pin,'Immutable review member '+name)
    s=importlib.util.spec_from_file_location('direct_native_metadata',HERE/'review.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);result=m.source(root)
    selected=json.loads((HERE/'selected.json').read_bytes())
    for mode,row in selected['final'].items():
        r=row['result'];need(r['mode']==mode and r['total_function_bytes']==382 and r['total_instructions']==138 and r['RELA']==0 and not r['undefined_symbols'],'Retained actual final native summary')
        need(len(r['actual_raw_controls'])==3 and all(x['rejected'] for x in r['actual_raw_controls']),'Retained bounded raw controls')
        need([r['entries'][k]['new_bytes'] for k in ('compare','fill','copy')]==[52,48,52],'Measured direct wrapper sizes')
        need(all(x['kernel']['normal_result_projection'] and not x['kernel']['full_original_register_ABI'] for x in r['entries'].values()),'Conditional projection separated from whole ABI')
    need((HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes(),'Default Traditional Chinese README')
    return dict(passed=True,sealed_members=len(seal['members']),seal_sha256=sha(HERE/'seal.json'),source=result,metadata_only=True,actual_native_artifacts_read=False,target_execution=False,physical_ABI_proved=False,installed_provider_proved=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);a=p.parse_args();print(json.dumps(check(a.project_root.resolve())))
