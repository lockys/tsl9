#!/usr/bin/env python3
"""Read-only review replay; compilation and target execution are never invoked."""
import argparse
import collections
import hashlib
import importlib.util
import json
from pathlib import Path

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def need(value,message):
    if not value:raise ValueError(message)
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def load(path):
    spec=importlib.util.spec_from_file_location('reviewed_image_runner',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--firmware',type=Path)
    parser.add_argument('--artifact-root',type=Path,help='Optional original fresh-build folder containing c/cpp; replay also requires its recorded local tools and paths')
    args=parser.parse_args();project=args.project_root.resolve(strict=True);root=Path(__file__).resolve().parent
    report=read(root/'review.json')
    for item in report['reviewed_inputs']:
        target=(project/item['path']).resolve(strict=True);target.relative_to(project)
        need(sha(target)==item['sha256'],'Reviewed input hash: '+item['path'])
    runner_path=root.parent/'integration/verify_image.py'
    need(sha(runner_path)==report['runner_sha256'],'Reviewed actual runner identity')
    runner=load(runner_path);ctx=runner.context(project);manifest=ctx['manifest']
    need(len(manifest['source_units'])==34 and len(manifest['source_files'])==73,'34 original units and 73 original source/header inputs')
    need(len(manifest['allocations'])==691 and len(manifest['section_relative_bindings'])==53,'Original ownership and relative label count')
    need([(x['originalVA'],x['bytes']) for x in manifest['selected_sections']]==[(0x9a42,144),(0x19124,30),(0x19142,30),(0x19160,30),(0x1917e,30)],'Exact five selected extents')
    need(manifest['retained_RELA_count']==8270,'Outside relocation multiplicity')
    firmware,original=ctx['CF'].original_image(project,ctx['cf'],args.firmware)
    need(sha(firmware)==manifest['original_image_sha256'],'Original firmware identity')
    candidate=bytearray(original)
    for item in manifest['expected_differences']:
        offset=item['address']-0x8000;need(candidate[offset]==item['original'],'Admitted original changed byte')
        candidate[offset]=item['native']
    need(hashlib.sha256(candidate).hexdigest()==report['candidate_image_sha256'],'Pure source-backed expected image hash; no output image written')
    need(len(candidate)==76800 and sum(a!=b for a,b in zip(candidate,original))==8,'Exact whole-image diff count')
    controls=0;modes=set()
    for item in report['selected_receipts']:
        path=(root/item['path']).resolve(strict=True);path.relative_to(root)
        need(sha(path)==item['sha256'],'Actual selected receipt hash')
        value=read(path);modes.add(value['mode'])
        need(value['passed'] is True and value['runner_sha256']==report['runner_sha256'],'Final actual runner success')
        need(value['source_files']==manifest['source_files'],'Exact source pins in selected receipt')
        need(value['checks']['image']['sha256']==report['candidate_image_sha256'],'Actual compiled image hash')
        need(value['checks']['image']['differences']==manifest['expected_differences'],'All eight actual changed byte values')
        need(value['checks']['native_dependency_closure']['dependency_rules']==36 and value['checks']['native_dependency_closure']['pinned_native_files']==71,'Compiler-observed application dependency closure')
        need(value['checks']['actual_commands']=={'commands':44,'compile_TUs':36,'strict_missing_ROM_rejected':True},'Actual exact compile/link/export records')
        need(len(value['artifacts'])==144 and len(value['commands'])==44,'Artifact and command inventories')
        need(len(value['actual_negative_controls'])==15 and all(x['rejected'] for x in value['actual_negative_controls']),'Actual retained negative controls')
        need(all(value[k] is False for k in ('strict_ROM_provider','pointwise_equivalence','asynchronous_equivalence','flashable','OTA_ready','hardware','network','target_execution','emulation')),'Explicit evidence limits')
        controls+=len(value['actual_negative_controls'])
        if args.artifact_root:
            archived=args.artifact_root.resolve(strict=True)/value['mode']/'verification.json'
            need(sha(archived)==item['sha256'],'Actual archived original receipt bytes')
            runner.replay(project,archived,ctx,original)
            image=archived.parent/'NOT-FLASH-VALIDATED-irq-callframe.bin'
            need(image.read_bytes()==candidate,'Independent whole-image byte comparison')
    need(modes=={'c','cpp'},'Actual final C and C++ runs')
    checksum=read(root/'checksum-note.json')
    block=checksum['raw_plaintext_block_index'];start=block*1024
    before=original[start:start+1024];after=candidate[start:start+1024]
    need(block==6 and sum(before)&65535==checksum['original_data_sum16'] and sum(after)&65535==checksum['candidate_data_sum16'],'Recomputed bounded plaintext additive sums')
    need(collections.Counter(before)==collections.Counter(after) and before!=after,'Permutation preserves sum, not byte identity')
    reference_inputs=[]
    for key in ('APK_evidence','ID2966_native_evidence'):
        item=checksum[key];path=project/item['path']
        if path.is_file():need(sha(path)==item['sha256'],'Available checksum-reference source identity')
        reference_inputs.append({'reference':key,'available_and_hash_checked':path.is_file()})
    if (root/'seal.json').is_file():
        for item in read(root/'seal.json')['members']:
            target=(root/item['path']).resolve(strict=True);target.relative_to(root)
            need(sha(target)==item['sha256'] and target.stat().st_size==item['bytes'],'Review sealed member')
    print(json.dumps({'passed':True,'selected_fresh_modes':2,'actual_negative_controls_rejected':controls,'whole_archived_artifacts_replayed':bool(args.artifact_root),'candidate_bytes':76800,'candidate_diff_bytes':8,'checksum_reference_inputs':reference_inputs,'partial_readable_C_only':True,'flashable':False,'OTA_ready':False,'target_execution':False},sort_keys=True))
if __name__=='__main__':main()
