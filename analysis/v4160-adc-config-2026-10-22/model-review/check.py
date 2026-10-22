#!/usr/bin/env python3
"""Sealed ADC independent review metadata; no compilation, launch or build read."""
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
    for name,pin in seal['members'].items():need(sha(HERE/name)==pin,'Exact sealed independent review member '+name)
    s=importlib.util.spec_from_file_location('adc_metadata_native',HERE/'native.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);result=m.stable(root)
    producer=m.source().case(root,'v4160-adc-config-2026-10-22')/'implementation/probe.py';need(sha(producer)==json.loads((HERE/'reference-pins.json').read_bytes())['producer'],'Frozen producer reader identity')
    data=json.loads((HERE/'selected.json').read_bytes());need(set(data['native'])==set(data['host'])=={'c','cpp'},'Both actual retained languages')
    for mode in('c','cpp'):
        h=data['host'][mode];n=data['native'][mode]
        need(h['tests']==dict(passed=True,cases=74,checks=2904,ordered_effects=14,synthetic_IO=True,RV32_execution=False) and h['compiled_controls']==3,'Independent actual HOST coverage')
        need(n['selected']['bytes']==102 and n['selected']['instructions']==38 and n['selected']['additional_own_written_GPRs']==[12,16,17] and not n['selected']['full_original_register_ABI'],'Measured actual native size and remaining register ABI differences')
        need(n['total_function_bytes']==254 and n['total_instructions']==93 and len(n['functions'])==5 and n['RELA']==0 and not n['undefined_symbols'],'All actual five global functions included')
        need(len(n['actual_controls'])==5 and all(x['rejected'] for x in n['actual_controls']),'Three actual raw and two IR controls')
        need(not n['target_execution'] and not n['ISA_emulation'] and not n['linked'] and not n['BIN_exported'] and not n['physical_ABI_proved'],'No execution or physical admission')
    need(data['native']['c']['object_sha256']==data['native']['cpp']['object_sha256'],'Actual C/C++ complete objects match')
    need((HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes(),'Default Traditional Chinese documentation')
    return dict(passed=True,seal_sha256=sha(HERE/'seal.json'),sealed_members=len(seal['members']),source=result,retained_HOST_cases_per_language=74,retained_native_object_count=2,metadata_only=True,actual_HOST_artifacts_read=False,actual_native_artifacts_read=False,target_execution=False,physical_ABI_proved=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);a=p.parse_args();print(json.dumps(check(a.project_root.resolve())))
