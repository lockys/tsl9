#!/usr/bin/env python3
"""Portable static Flash GPR/instruction-frontier review; target execution is absent."""
import argparse
import importlib.util
import json
from pathlib import Path
import frontier as F

HERE=Path(__file__).resolve().parent
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
def run(root,firmware,candidate=None,require_leaf_frontiers=False,folder=None,require_exact_leaves=False,receipt=None):
    decode,source,raw,negatives=F.source(root,firmware);reference=F.read(HERE/'baseline.json');old=[]
    source_audit=module('register_prefix_source_audit',HERE/'source-audit.py').inspect(root)
    for r in reference['functions']:
        entry=r['entry'];original=raw[entry-0x8000:entry-0x8000+r['bytes']];comparison=F.compare(original,bytes.fromhex(r['current_hex']),entry,decode);F.need(comparison==r['comparison'],'Exact source/current frontier reference');old.append(comparison)
    report={'schema':'ID2966-independent-flash-register-prefix-review-v1','passed':True,'raw_source_and20controls_rechecked':True,'current_original_archive_replayed':False,'current_reference_image_sha256':reference['current_image_sha256'],'candidate_artifacts_read':False,'current_frontier_equal_entries':[r['entry'] for r in old if r['same_decoded_instruction_frontiers_modulo_commutative_sources']],'current_source_audit':source_audit,'actual_archived_artifacts_replayed':False,'target_execution':False,'emulation':False,'network':False,'hardware':False,'fault_interrupted_execution_validated':False,'whole_wrapper_pointwise_equivalence':False,'ROM_provider':False,'flashable':False,'OTA_ready':False}
    if candidate:
        bodies=F.component_bodies(root,candidate);results=[F.compare(raw[entry-0x8000:entry-0x8000+size],bodies[entry],entry,decode) for entry,size in F.RANGES]
        if require_leaf_frontiers:F.need(all(r['same_decoded_instruction_frontiers_modulo_commutative_sources'] for r in results if r['entry']!=0x9c0a),'Every leaf original decoded instruction frontier restored')
        if require_exact_leaves:F.need(all(r['exact_original_bytes'] for r in results if r['entry']!=0x9c0a),'All198 leaf bytes identical to original')
        report.update(candidate_artifacts_read=True,candidate_ELF_sha256=F.sha(candidate),candidate_results=results,all_five_leaf_frontiers_restored=all(r['same_decoded_instruction_frontiers_modulo_commutative_sources'] for r in results if r['entry']!=0x9c0a),all_five_leaves_byte_identical=all(r['exact_original_bytes'] for r in results if r['entry']!=0x9c0a))
        if folder:
            report['actual_partial_objects']=F.partial_objects(root,folder,bodies,decode,source['ledger'])
            spec=importlib.util.spec_from_file_location('prefix_IR_review',HERE/'ir-review.py');ir=importlib.util.module_from_spec(spec);spec.loader.exec_module(ir)
            report['actual_IR']=[ir.inspect(name,(folder/(name+'.ll')).read_text(encoding='utf-8')) for name in ('quarter','status','unlock','lock','erase','program')]
    if receipt:
        runner=F.case(root,'v4160-flash-register-prefix-2026-10-22')/'implementation/verify_native.py';report['producer_readonly_replay']=module('prefix_final_native_runner',runner).replay(root,receipt,firmware);report['actual_archived_artifacts_replayed']=True
    if (HERE/'seal.json').exists():
        for name,pin in F.read(HERE/'seal.json')['members'].items():F.need(F.sha(HERE/name)==pin['sha256'] and (HERE/name).stat().st_size==pin['bytes'],'Immutable prefix review '+name)
        report['sealed_members_checked']=True
    return report
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,required=True);p.add_argument('--firmware',type=Path,required=True);p.add_argument('--receipt',type=Path);p.add_argument('--candidate-elf',type=Path);p.add_argument('--candidate-folder',type=Path);p.add_argument('--require-leaf-frontiers',action='store_true');p.add_argument('--require-exact-leaves',action='store_true');p.add_argument('--output',type=Path);a=p.parse_args();F.need(sum(bool(x) for x in (a.receipt,a.candidate_folder,a.candidate_elf))<=1,'Choose an actual receipt, complete folder or single linked ELF');folder=a.receipt.parent if a.receipt else a.candidate_folder;candidate=folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf' if folder else a.candidate_elf;F.need(not(a.require_leaf_frontiers or a.require_exact_leaves) or candidate,'Required leaf gate needs actual component');r=run(a.project_root.resolve(),a.firmware.resolve(),candidate.resolve() if candidate else None,a.require_leaf_frontiers,folder.resolve() if folder else None,a.require_exact_leaves,a.receipt.resolve() if a.receipt else None)
    if a.output:
        out=a.output.resolve();out.relative_to(HERE);F.need(not out.exists(),'Create-only independent review');out.write_bytes((json.dumps(r,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(r if not a.output else {'passed':True,'output':str(a.output),'candidate_artifacts_read':r['candidate_artifacts_read']}))
if __name__=='__main__':main()
