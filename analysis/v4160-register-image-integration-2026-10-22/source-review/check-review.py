#!/usr/bin/env python3
"""Portable independent source/compile/ABI-scheduling/ELF/LOAD/BIN review."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode=True

HERE=Path(__file__).resolve().parent
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
G=module('new_whole_image_context',HERE/'image-gate.py')
def inspect(root,firmware,receipt=None):
    root=Path(root).resolve(strict=True);firmware=Path(firmware).resolve(strict=True);pins=G.read(HERE/'review-inputs.json');c=G.context(root,firmware,pins['manifest_sha256']);runner=HERE.parent/'implementation/verify_image.py';G.need(G.sha(runner)==pins['producer_runner_sha256'],'Final reviewed wholeimage runner')
    result={'schema':'ID2966-independent-register-scheduled-image-review-v1','passed':True,'manifest_sha256':pins['manifest_sha256'],'producer_runner_sha256':pins['producer_runner_sha256'],'current_native_source_inputs_checked':76,'current_scheduling_inputs_checked':10,'expected_image_sha256':G.sha(firmware),'original_baseline_archives_replayed':False,'actual_archived_artifacts_replayed':False,'actual_source_compile_provenance_replayed':False,'compiler_alone_emitted_scheduled_order':False,'pipeline':'C/C++ compiler output plus explicit source-owned ABI scheduling','original_BIN_is_generation_input':False,'new_user_features_implemented':False,'target_execution':False,'emulation':False,'network':False,'hardware':False,'ROM_provider':False,'physical_compatibility_proved':False,'asynchronous_equivalence_proved':False,'flashable':False,'OTA_ready':False}
    if receipt:
        receipt=Path(receipt).resolve(strict=True);r=G.read(receipt);folder=receipt.parent;G.need(r['runner_sha256']==pins['producer_runner_sha256'] and r['manifest_sha256']==pins['manifest_sha256'] and r['firmware_sha256']==G.sha(firmware),'Current actual receipt identity')
        result['actual_source_compile_provenance']=module('independent_new_source_provenance',HERE/'provenance.py').inspect(root,folder,r,c)
        result['actual_frame_chain']=module('independent_new_frame_chain',HERE/'frame-chain.py').inspect(root,folder,c)
        result['actual_image']=c['G'].artifact_gate(c['E'](folder/'source-integrated.o'),c['E'](folder/'ADDRESS-WITNESS-ONLY.elf'),folder/'NOT-FLASH-VALIDATED-register-scheduled.bin',c)
        prefix=G.case(root,'v4160-flash-register-prefix-2026-10-22')/'source-review';meta=G.read(prefix/'seal.json')['members']['ir-review.py'];G.need(G.sha(prefix/'ir-review.py')==meta['sha256'],'Immutable independent source/register IR gate');ir=module('independent_closed_prefix_IR',prefix/'ir-review.py');result['actual_readable_Flash_IR']=[ir.inspect(name,(folder/('flash-'+name+'.ll')).read_text(encoding='utf-8')) for name in ('quarter','status','unlock','lock','erase','program')]
        result['producer_static_replay']=module('current_producer_readonly_replay',runner).replay(root,receipt,firmware)
        result.update(actual_archived_artifacts_replayed=True,actual_source_compile_provenance_replayed=True,actual_receipt_sha256=G.sha(receipt),mode=r['mode'])
    if (HERE/'seal.json').exists():
        for name,pin in G.read(HERE/'seal.json')['members'].items():G.need(G.sha(HERE/name)==pin['sha256'] and (HERE/name).stat().st_size==pin['bytes'],'Immutable independent review member '+name)
        result['sealed_members_checked']=True
    return result
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,required=True);p.add_argument('--firmware',type=Path,required=True);p.add_argument('--receipt',type=Path);p.add_argument('--output-report',type=Path);a=p.parse_args();r=inspect(a.project_root,a.firmware,a.receipt)
    if a.output_report:
        out=a.output_report.resolve();out.relative_to(HERE);G.need(not out.exists(),'Create-only independent readback report');out.write_bytes((json.dumps(r,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(r if not a.output_report else {'passed':True,'output':str(a.output_report),'actual_archived_artifacts_replayed':r['actual_archived_artifacts_replayed']}))
if __name__=='__main__':main()
