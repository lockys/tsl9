#!/usr/bin/env python3
"""Read-only sealed metadata verification; no native rebuild or execution."""
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
    s=importlib.util.spec_from_file_location('register_independent',HERE/'review.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);result=m.source(root)
    retained=json.loads((HERE/'selected.json').read_bytes());need(set(retained)=={'compare','fill','copy'},'Exactly three fixed masks')
    sizes={'compare':60,'fill':68,'copy':64};counts={'compare':23,'fill':24,'copy':22};totals={'compare':454,'fill':492,'copy':418}
    for leaf,modes in retained.items():
        need(set(modes)=={'c','cpp'},'Both actual languages retained')
        need(modes['c']['object_sha256']==modes['cpp']['object_sha256'],'C/C++ whole actual objects identical')
        for mode,r in modes.items():
            s=r['selected'];need(r['mode']==mode and r['leaf']==leaf and s['new_bytes']==sizes[leaf] and r['total_function_bytes']==totals[leaf],'Retained actual full/selected sizes')
            need(next(f['instructions'] for f in r['functions'] if f['name']==s['name'])==counts[leaf],'Selected actual instruction coverage')
            need(len(r['functions'])==11 and r['unused_genuine_global_functions']==10 and r['RELA']==0 and not r['undefined_symbols'],'All actual functions, UND0, RELA0')
            need(s['new_frame_bytes']==16 and s['RA_SP_own_written'] and s['previous_extra_allocator_writes_removed'],'Removed allocator extras accompanied by real frame/RA/SP regression')
            need(len(r['actual_controls'])==3 and all(x['rejected'] for x in r['actual_controls']),'Actual raw and selected IR controls rejected')
            need(not r['physical_ABI_proved'] and not s['kernel']['full_original_register_ABI'] and not r['target_execution'] and not r['ISA_emulation'] and not r['linked'] and not r['BIN_exported'],'No false admission or target execution')
    need((HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes(),'Default Traditional Chinese README')
    return dict(passed=True,sealed_members=len(seal['members']),seal_sha256=sha(HERE/'seal.json'),source=result,metadata_only=True,actual_native_artifacts_read=False,native_fixed_bank_recipes=3,retained_actual_objects=6,new_frames_bytes=[16,16,16],physical_ABI_proved=False,target_execution=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);a=p.parse_args();print(json.dumps(check(a.project_root.resolve())))
