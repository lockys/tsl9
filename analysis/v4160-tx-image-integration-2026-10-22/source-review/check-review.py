#!/usr/bin/env python3
"""Source/reference default; explicit receipt replays actual full source provenance."""
import argparse
from pathlib import Path
import json
import importlib.util
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent

def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def inspect(root,firmware,receipt=None):
    R=load('thirteen_source_roles',HERE/'roles.py');root=Path(root).resolve(strict=True);firmware=Path(firmware).resolve(strict=True)
    if (HERE/'seal.json').exists():
        for name,pin in R.read(HERE/'seal.json')['members'].items():
            p=(HERE/name).resolve(strict=True);p.relative_to(HERE);R.need(R.sha(p)==pin,'Immutable independent review member '+name)
    root,E,decode,ref=R.metadata(root,firmware);P=load('thirteen_source_provenance',HERE/'provenance.py');source=P.context(R,root,firmware);pins=R.read(HERE/'review-inputs.json');model=root/'experiments/tsl9-v4160-tx-image-integration';R.need(R.sha(model/'source-manifest.json')==pins['manifest_sha256'],'Reviewed frozen source manifest')
    producer=R.case(root,'v4160-tx-image-integration-2026-10-22')/'implementation/verify_image.py';abi=R.case(root,'v4160-tx-image-integration-2026-10-22')/'ABI-review/review.py';R.need(R.sha(producer)==pins['producer_runner_sha256'] and R.sha(abi)==pins['ABI_checker_sha256'],'Final reviewed producer/independent ABI checker')
    for name,pin in pins['producer_dependency_pins'].items():R.need(R.sha(producer.parent/name)==pin,'Reviewed actual source generator/order driver '+name)
    result=dict(schema='ID2966-thirteen-image-independent-source-review-v1',passed=True,original_regions=13,actual_provider_FUNCTIONS=15,typed_owned_bytes=930,TX_real_FUNC_bytes=[8,270,2],current_source_pins=85,old_source_reference_RELA=8258,original_TX_private_control_roles=7,original_TX_private_PCREL_roles=1,original_raw_external_incoming_rechecked=9,actual_archived_artifacts_replayed=False,actual_source_compile_provenance_replayed=False,actual_ABI_LOAD_image_replayed=False,baseline_archived_object_required=False,compiler_only=False,whole_original_ABI_admitted=False,asynchronous_equivalence=False,computed_interior_reference_absence=False,ROM_provider=False,hardware=False,flashable=False,OTA_ready=False,target_execution=False,ISA_emulation=False,network=False)
    if receipt:
        receipt=Path(receipt).resolve(strict=True);r=R.read(receipt);R.need(r['passed'] and r['runner_sha256']==pins['producer_runner_sha256'] and r['manifest_sha256']==pins['manifest_sha256'] and r['firmware_sha256']==R.FW,'Actual selected current source/compiler identities')
        folder=receipt.parent;proof=P.inspect(R,root,firmware,folder,r);roles=R.actual(root,firmware,folder);byte=load('thirteen_role_countercases',HERE/'countercases.py').inspect(R,root,firmware,folder);recipes=load('thirteen_recipe_countercases',HERE/'recipe-controls.py').inspect(R,P,root,firmware,folder,r)
        a=load('thirteen_actual_independent_ABI',abi).inspect(root,folder,firmware);p=load('thirteen_actual_producer_replay',producer).replay(root,receipt,firmware);R.need(a['static_full_image_contract_passed'] and a['actual_build_artifact_replay'] and p['passed'],'Actual independent ABI and producer replay passed')
        result.update(actual_archived_artifacts_replayed=True,actual_source_compile_provenance_replayed=True,actual_ABI_LOAD_image_replayed=True,mode=r['mode'],receipt_sha256=R.sha(receipt),actual_artifact_count=len(r['artifacts']),source_provenance=proof,source_role_proof=roles,focused_actual_byte_controls=byte,focused_recipe_dependency_controls=recipes,actual_independent_ABI_passed=True,actual_producer_replay_passed=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--firmware',required=True,type=Path);p.add_argument('--receipt',type=Path);a=p.parse_args();print(json.dumps(inspect(a.project_root,a.firmware,a.receipt)))
