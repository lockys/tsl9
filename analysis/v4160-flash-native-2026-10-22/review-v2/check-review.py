#!/usr/bin/env python3
"""Read-only current-runner review; retained test receipts are not fresh execution."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

OLD_SEAL='173c8790e2deaad0ae6ac29bea2cabdbc8be2c13b68edefc3d5beb37c545488c'
OLD_RUNNER='d1f470a8539eb9815eaa65230a6da974f7dd21b2c009950516e0e3d250cc377e'
MODEL='experiments/tsl9-v4160-flash-native'

def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def load(name,p):
    spec=importlib.util.spec_from_file_location(name,p)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def seal_members(folder,pin):
    need(sha(folder/'seal.json')==pin,'Exact retained seal '+str(folder))
    for row in read(folder/'seal.json')['members']:
        p=(folder/row['path']).resolve(strict=True);p.relative_to(folder.resolve())
        need(p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],'Immutable sealed member '+row['path'])
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root',required=True,type=Path)
    parser.add_argument('--firmware',type=Path)
    parser.add_argument('--archive-root',type=Path,help='Optional retained v2 host build root; no binaries are executed during replay')
    args=parser.parse_args();project=args.project_root.resolve(strict=True)
    here=Path(__file__).resolve().parent;case=here.parent;old=case/'review'
    report=read(here/'review.json');seal_members(old,OLD_SEAL)
    need(report['old_review_seal_sha256']==OLD_SEAL and report['old_host_runner_sha256']==OLD_RUNNER,'Explicit immutable historical binding')
    previous=read(old/'review.json')
    for row in previous['model_inputs']:
        if row['path']==MODEL+'/verify_host.py':
            need(row['sha256']==OLD_RUNNER,'Explicit historical runner pin');continue
        need(sha(project/row['path'])==row['sha256'],'Unchanged reused model/helper '+row['path'])
    for row in previous['case_inputs']:
        need(sha(case/row['path'])==row['sha256'],'Unchanged native checker '+row['path'])
    for row in report['current_inputs']:
        p=(project/row['path']).resolve(strict=True);p.relative_to(project)
        need(sha(p)==row['sha256'],'Exact current review input '+row['path'])
    runner_path=project/MODEL/'verify_host.py'
    need(sha(runner_path)==report['runner_sha256'] and sha(runner_path)!=OLD_RUNNER,'V2 runner explicitly supersedes the old pinned runner')
    seal_members(case/'source',previous['source_seal_sha256'])
    raw_checked=False
    if args.firmware:
        raw=args.firmware.read_bytes()
        need(len(raw)==76800 and hashlib.sha256(raw).hexdigest()==previous['original_firmware_sha256'],'Exact original ID2966 raw data')
        decoder=load('v2_original_static_decoder',case/'source/inspect.py');proof=read(case/'source/source-proof.json')
        need(decoder.facts(raw)==proof['ledger'],'All262 original bytes/99 source rows')
        need(len(proof['raw_negatives'])==20,'Twenty actual source controls')
        for control in proof['raw_negatives']:
            changed=bytearray(raw);offset=control['PC']-0x8000;replacement=bytes.fromhex(control['after'])
            need(changed[offset:offset+len(replacement)].hex()==control['before'],'Raw negative original anchor')
            changed[offset:offset+len(replacement)]=replacement
            try:decoder.facts(changed)
            except ValueError:pass
            else:raise ValueError('Original source control accepted '+control['name'])
        raw_checked=True
    modes=set();runner=load('v2_current_host_runner',runner_path)
    for selected in report['host_receipts']:
        p=here/selected['path'];need(sha(p)==selected['sha256'],'Exact selected fresh v2 host receipt')
        receipt=read(p);modes.add(receipt['mode'])
        need(receipt['passed'] and receipt['runner_sha256']==report['runner_sha256'],'Current runner produced this host result')
        need(receipt['tests']=={'passed':True,'groups':5,'cases':481,'checks':247191,'synthetic_provider':True,'RV32_execution':False},'Exact frozen host coverage')
        need(receipt['source_sha256']=={p.relative_to(project/MODEL).as_posix():sha(p) for d in ('src','tests') for p in (project/MODEL/d).glob('*') if p.is_file()},'Exact unchanged source/test reuse')
        need(len(receipt['actual_compiled_controls'])==6 and all(c['compiled'] and c['rejected'] for c in receipt['actual_compiled_controls']),'Six actual compiled behavior controls per language')
        positive=receipt['commands'][1]['host_executable_guard']
        need(positive['format']=='PE' and positive['machine']==0x8664 and positive['bits']==64 and positive['host_arch']=='x86_64' and positive['host_platform']=='win32','Actual guarded Windows host admission')
        need(positive['sha256']==receipt['executable_sha256'],'Actual positive executable hash is the guarded one')
        for control in receipt['actual_compiled_controls']:
            guard=control['commands'][1]['host_executable_guard']
            need(all(guard[k]==positive[k] for k in ('format','machine','bits','host_arch','host_platform')),'Each actual behavior-negative launch has a matching host guard')
            need(guard['sha256']==control['executable_sha256'],'Actual negative executable hash is the guarded one')
        if args.archive_root:
            original=args.archive_root/selected['archive_path'];need(sha(original)==selected['sha256'],'Actual retained v2 receipt')
            runner.replay(project,original)
    need(modes=={'c','cpp'},'Both fresh v2 host languages')
    for row in report['audit_receipts']:
        need(sha(here/row['path'])==row['sha256'],'Independent guard audit receipt')
        observation=read(here/row['path'])
        need(observation['passed'] and observation['target_execution'] is False,'Guard-only observation, no RV32 execution')
        need(observation['runner_sha256']==report['runner_sha256'],'Guard observation binds final current runner')
        need(observation['RV32_subprocess_calls']==0 and observation['actual_RV32_ELF']['machine']==243 and observation['actual_RV32_ELF']['bits']==32,'Actual RV32 rejected before process spawning')
        need(observation['old_checker_rejected_new_runner'] and observation['host_architecture_from_current_python_only'],'Explicit old runner supersession and interpreter-derived architecture')
        need(observation['actual_host_PE']==observation['empty_platform_machine_admission'],'No dependence on missing platform.machine value')
    need(all(report[k] is False for k in ('target_execution','ISA_emulation','hardware','network','new_firmware_BIN','OTA_ready')),'Evidence boundaries remain false')
    if (here/'seal.json').is_file():
        seal_members(here,sha(here/'seal.json'))
    print(json.dumps({'passed':True,'raw_source_and20controls_rechecked':raw_checked,'actual_archived_artifacts_replayed':bool(args.archive_root),'old_review_17members_preserved':True,'old_host_runner_superseded':True,'historical_independent_effects_reexecuted':False,'historical_native_recompiled':False,'new_firmware_BIN':False,'target_execution':False,'OTA_ready':False},sort_keys=True))
if __name__=='__main__':main()
