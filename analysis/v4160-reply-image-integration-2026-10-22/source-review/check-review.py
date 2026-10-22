#!/usr/bin/env python3
"""Metadata/source default, optional actual compiler+ABI+image archive readback."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
MANIFEST='2bac53620548772e2e06197dd52b9e0ca6e50a7f88d27b6f39fd1fddf2ac3f78'
PLAN='ddac5dcc40bd6395fa783e98f278b494eac3ac9988ecf5fecdeb92ed9cee3694'
FW='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
def need(value,message):
    if not value:raise ValueError(message)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def closure():
    if (HERE/'seal.json').exists():
        for name,pin in read(HERE/'seal.json')['members'].items():
            path=(HERE/name).resolve(strict=True);need(path.parent==HERE and sha(path)==pin,'Immutable independent source review member '+name)
def inspect(root,firmware,receipt=None):
    root=Path(root).resolve(strict=True);firmware=Path(firmware).resolve(strict=True);closure();pins=read(HERE/'review-inputs.json');need(sha(firmware)==FW and firmware.stat().st_size==76800,'Exact original source-reference payload')
    source=load('twelve_source_context',HERE/'source-inputs.py');model=root/'experiments/tsl9-v4160-reply-image-integration';c=source.context(root,model/'source-manifest.json',MANIFEST)
    plan=HERE.parent/'image-plan';need(sha(plan/'seal.json')==PLAN,'Immutable twelve-function source plan')
    for row in read(plan/'seal.json')['members']:
        path=(plan/row['path']).resolve(strict=True);path.relative_to(plan);need(sha(path)==row['sha256'] and path.stat().st_size==row['bytes'],'Immutable source plan member')
    producer=HERE.parent/'implementation/verify_image.py';abi=HERE.parent/'ABI-review/review.py';need(sha(producer)==pins['producer_runner_sha256'],'Final reviewed producer runner');need(sha(abi)==pins['ABI_checker_sha256'],'Final independent ABI/image checker')
    call=load('twelve_corrected_incoming_call',source.case(root,'v4160-ota-page-reply-2026-10-22')/'entry-call-correction/check.py').inspect(root,firmware)
    result={'schema':'ID2966-twelve-image-independent-source-review-v1','passed':True,'current_native_project_inputs_checked':79,'filtered_source_outputs_independently_reconstructed':5,'original_reference_bytes':76800,'incoming_9DF4_C_JAL_raw_rechecked':True,'selected_actual_commands_each':61,'selected_actual_object_TUs_each':43,'selected_existing_project_inputs_each':74,'selected_generated_inputs_each':14,'selected_compiler_resource_headers_each':1,'selected_focused_recipe_dependency_controls_each':13,'actual_archived_artifacts_replayed':False,'actual_compiler_resource_headers_rechecked':False,'actual_source_compile_provenance_replayed':False,'actual_ABI_LOAD_image_replayed':False,'compiler_alone_emitted_final_order':False,'original_BIN_is_codegen_input':False,'full_readable_firmware_claimed':False,'global_C_ABI_claimed':False,'target_execution':False,'ISA_emulation':False,'network':False,'hardware':False,'ROM_provider':False,'asynchronous_equivalence':False,'flashable':False,'OTA_ready':False}
    if receipt:
        receipt=Path(receipt).resolve(strict=True);r=read(receipt);need(r['passed'] and r['mode'] in ('c','cpp') and r['runner_sha256']==pins['producer_runner_sha256'] and r['manifest_sha256']==MANIFEST and r['firmware_sha256']==FW,'Current actual receipt mode/source/profile identities')
        gate=load('twelve_actual_provenance',HERE/'provenance.py');folder=receipt.parent;provenance=gate.inspect(root,folder,r,c,firmware);controls=load('twelve_actual_source_controls',HERE/'countercases.py').inspect(gate,root,folder,r,c,firmware);abi_result=load('twelve_actual_independent_ABI',abi).inspect(root,folder,firmware);producer_result=load('twelve_current_producer_replay',producer).replay(root,receipt,firmware)
        result.update(actual_archived_artifacts_replayed=True,actual_compiler_resource_headers_rechecked=True,actual_source_compile_provenance_replayed=True,actual_ABI_LOAD_image_replayed=True,receipt_sha256=sha(receipt),mode=r['mode'],actual_artifact_count=len(r['artifacts']),actual_source_provenance=provenance,focused_controls=controls,ABI_checker_passed=bool(abi_result['passed']),producer_replay_passed=bool(producer_result['passed']))
    return result
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--project-root',type=Path,required=True);parser.add_argument('--firmware',type=Path,required=True);parser.add_argument('--receipt',type=Path);parser.add_argument('--output-report',type=Path);args=parser.parse_args();result=inspect(args.project_root,args.firmware,args.receipt)
    if args.output_report:
        path=args.output_report.resolve();path.relative_to(HERE/'build');need(not path.exists(),'Create-only local independent report');path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((json.dumps(result,indent=2)+'\n').encode('utf-8'));print(json.dumps({'passed':True,'report':str(path),'sha256':sha(path),'actual_archived_artifacts_replayed':result['actual_archived_artifacts_replayed']}))
    else:print(json.dumps(result))
if __name__=='__main__':main()
