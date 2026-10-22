#!/usr/bin/env python3
"""Sealed caller-bank metadata verification; no actual build read or execution."""
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
    for path,pin in seal['members'].items():need(sha(HERE/path)==pin,'Immutable independent member '+path)
    s=importlib.util.spec_from_file_location('caller_metadata',HERE/'review.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);original=m.stable(root)
    need(sha(m.case(root,'v4160-adc-caller-2026-10-22')/'implementation/probe.py')==json.loads((HERE/'reference-pins.json').read_bytes())['producer'],'Frozen producer source')
    data=json.loads((HERE/'selected.json').read_bytes());need(set(data)=={'c','cpp'},'Two actual language records')
    for mode,r in data.items():
        need(r['mode']==mode and r['selected']['bytes']==110 and r['selected']['instructions']==42 and r['selected']['written_GPRs']==[1,2,12,13,14,15,16],'Actual selected110B/42-row register state')
        need(r['total_function_bytes']==266 and r['total_instructions']==103 and len(r['functions'])==5 and r['unused_genuine_global_functions']==4,'Every actual global function retained')
        need(all(not x['fixed_GPR_writes'] for x in r['functions']) and r['RELA']==0 and not r['undefined_symbols'],'Actual complete mask honored; UND0/RELA0')
        p=r['normal_caller_projection'];need(p['conditionally_supported'] and p['callee_frame_bytes']==16 and p['existing_callback_stack_interval_bytes']==144 and p['public_A0_A1_unchanged'],'Only bounded normal caller projection')
        need(not p['full_original_callee_ABI'] and not p['fault_async_IRQ_equivalence'] and not p['placement_proved'] and not p['flashability_proved'],'No broader equivalence or placement admission')
        need(len(r['actual_controls'])==5 and all(x['rejected'] for x in r['actual_controls']),'Three raw and two IR control rejections')
        need(not r['target_execution'] and not r['ISA_emulation'] and not r['linked'] and not r['BIN_exported'] and not r['physical_ABI_proved'],'No execution/link/BIN/physical claim')
    need(data['c']['object_sha256']==data['cpp']['object_sha256'],'Actual C/C++ entire objects identical')
    need((HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes(),'Default Traditional Chinese README')
    return dict(passed=True,seal_sha256=sha(HERE/'seal.json'),sealed_members=len(seal['members']),source=original,metadata_only=True,actual_native_artifacts_read=False,retained_actual_objects=2,specific_caller_normal_projection_conditionally_supported=True,full_original_callee_ABI_proved=False,physical_ABI_proved=False,target_execution=False,HOST_matrix_rerun=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);a=p.parse_args();print(json.dumps(check(a.project_root.resolve())))
