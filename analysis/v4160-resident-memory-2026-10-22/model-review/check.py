#!/usr/bin/env python3
"""Default is sealed metadata/source review, not actual build archive replay."""
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
def load(name):
    s=importlib.util.spec_from_file_location('resident_memory_'+name,HERE/name);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def check(root):
    seal=json.loads((HERE/'seal.json').read_bytes())
    for name,pin in seal['members'].items():need(sha(HERE/name)==pin,'Sealed member '+name)
    r=load('review.py');source=r.sources(root);core=json.loads((HERE/'core-pins.json').read_bytes())
    need(all(sha(root/r.MODEL/'src'/name)==pin for name,pin in core.items()),'Current authored four-file source identity')
    refs=json.loads((HERE/'reference-pins.json').read_bytes())
    need(sha(r.case(root,'v4160-resident-memory-2026-10-22')/'implementation/probe.py')==refs['producer'],'Current frozen native producer identity')
    for slug,key in [('v4160-config-lifetime-2026-10-22/memset-review','old_fill_source_seal'),('v4160-ota-handler-compact-2026-10-22/callee-review','old_copy_source_seal')]:need(sha(r.case(root,slug)/'seal.json')==refs[key],'Prior source-only seal identity')
    selected=json.loads((HERE/'selected.json').read_bytes())
    need(selected['HOST']['c']['tests']==selected['HOST']['cpp']['tests'] and selected['HOST']['c']['tests']['narrative_cases']==16 and selected['HOST']['c']['tests']['assertions']==940,'Retained independent narrative summary')
    need(all(x['compiled_semantic_controls']==3 for x in selected['HOST'].values()),'Retained actual compiled control summary')
    for mode,x in selected['native'].items():
        need(x['result']['mode']==mode and x['result']['allocated_bytes']==530 and x['result']['instructions']==218 and x['result']['RELA']==13 and x['result']['physical_ABI_proof'] is False and x['result']['installed_provider_proved'] is False,'Retained native observations and limits')
    need((HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes(),'Default Traditional Chinese README')
    return dict(passed=True,sealed_members=len(seal['members']),seal_sha256=sha(HERE/'seal.json'),source=source,
                metadata_only=True,actual_host_artifacts_replayed=False,actual_native_artifacts_read=False,
                target_execution=False,physical_ABI_proof=False,installed_provider_proved=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);a=p.parse_args();print(json.dumps(check(a.project_root.resolve())))
