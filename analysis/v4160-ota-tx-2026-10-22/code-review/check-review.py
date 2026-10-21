#!/usr/bin/env python3
"""Verify sealed source/model metadata; actual archived HOST replay is explicit."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
RAW_SEAL='d04462932608baac28bbd05704b63560f433bdd25c2e52c672a7e6e6b70a5b4b'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def need(v,m):
    if not v:raise ValueError(m)
def load(p,name):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def inspect(root,firmware,receipts=()):
    if (HERE/'seal.json').exists():
        for name,pin in read(HERE/'seal.json')['members'].items():
            p=(HERE/name).resolve(strict=True);need(p.parent==HERE and sha(p)==pin,'Immutable independent review '+name)
    raw=HERE.parent/'source-review-v2';need(sha(raw/'seal.json')==RAW_SEAL,'Original raw checker correction seal')
    proof=load(raw/'check-review.py','TX_original_source_for_host_review').inspect(root,firmware)
    runner=load(HERE/'run-effects.py','TX_independent_host_review');current=runner.inputs(root);selected=read(HERE/'selected-verification.json')
    need(current==selected['independent_inputs'],'Exact frozen core/oracle/runner/host-guard inputs')
    need({r['mode'] for r in selected['independent']}=={'c','cpp'},'Both independent languages retained')
    for row in selected['independent']:
        need(row['tests']=={'passed':True,'groups':4,'cases':31,'checks':78283,'target_execution':False} and row['actual_compiled_semantic_controls']==14 and row['receipt_controls_rejected']==10,'Exact selected actual synthetic evidence')
    need(sha(root/'experiments/tsl9-v4160-ota-tx/verify_host.py')==selected['producer']['runner_sha256'],'Reviewed producer HOST runner identity')
    replays=[runner.replay(root,Path(p).resolve()) for p in receipts]
    return {'passed':True,'source_bytes':280,'source_instruction_count':96,'raw_source_and40controls_rechecked':proof['raw_source_and40controls_rechecked'],'current_C_CPP_source_hashes_verified':True,'selected_independent_groups':4,'selected_independent_cases_per_language':31,'selected_independent_checks_per_language':78283,'selected_compiled_semantic_controls_per_language':14,'actual_archived_artifacts_replayed':bool(replays),'actual_HOST_receipt_replays':replays,'actual_target_execution':False,'ISA_emulation':False,'native_instruction_prefix_proved':False,'opaque_ROM_ABI_proved':False,'hardware':False,'OTA_ready':False}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,required=True);p.add_argument('--firmware',type=Path,required=True);p.add_argument('--receipt',type=Path,action='append',default=[]);a=p.parse_args();print(json.dumps(inspect(a.project_root.resolve(),a.firmware.resolve(),a.receipt)))
if __name__=='__main__':main()
