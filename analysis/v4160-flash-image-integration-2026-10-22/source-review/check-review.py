#!/usr/bin/env python3
"""Independent, data-only eleven-function image admission. Never executes target code."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
RUNNER_SHA='c4ed93b51f80038b88ec3a0847729d548323b667c04c7edce671f9e002a2805a'
REFERENCE_SHA='b1d2908c00fd7577beaf5cf9eee0a462cbe611767d310c7314ef945691da8ccf'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def sealed_members():
    path=HERE/'seal.json'
    if not path.exists():return False
    seal=json.loads(path.read_text(encoding='utf-8'))
    for name,pin in seal['members'].items():
        p=(HERE/name).resolve(strict=True);p.relative_to(HERE)
        need(sha(p)==pin['sha256'] and p.stat().st_size==pin['bytes'],'Immutable review member '+name)
    return True
def firmware_default(root):
    candidates=[root/'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin',root/'firmware/ID-2966-V4.1.60-decoded.bin']
    for path in candidates:
        if path.is_file():return path
    raise ValueError('Supply --firmware with exact original ID2966 image')
def inspect(root,firmware,receipt=None,artifacts=None,producer_replay=False):
    root=Path(root).resolve(strict=True);firmware=Path(firmware).resolve(strict=True)
    need(sha(HERE/'source-constraints.json')==REFERENCE_SHA,'Independent reference identity')
    g=load('independent_image_gate',HERE/'inspect-image.py');c=g.retained_context(root,firmware,HERE/'source-constraints.json')
    runner=HERE.parent/'implementation/verify_image.py';need(sha(runner)==RUNNER_SHA,'Final reviewed producer runner')
    report={'schema':'ID2966-independent-source-image-review-v1','passed':True,'sealed_review_members_checked':sealed_members(),'source_constraints_sha256':REFERENCE_SHA,'producer_runner_sha256':RUNNER_SHA,'current_project_source_pins_checked':76,'original_baseline_archives_replayed':False,'actual_new_artifacts_replayed':False,'actual_compilation_provenance_replayed':False,'producer_archive_replay':False,'independent_artifact_checks':None,'target_execution':False,'emulation':False,'network':False,'ROM_provider':False,'hardware':False,'OTA_ready':False,'flashable':False}
    if receipt:
        receipt=Path(receipt).resolve(strict=True);r=json.loads(receipt.read_text(encoding='utf-8'));folder=receipt.parent
        need(r['runner_sha256']==RUNNER_SHA and r['firmware_sha256']==sha(firmware),'Actual receipt runner/firmware identities')
        artifacts=[folder/'source-integrated.o',folder/'ADDRESS-WITNESS-ONLY.elf',folder/'NOT-FLASH-VALIDATED-irq-and-flash.bin']
        report['actual_compilation_provenance']=load('independent_provenance',HERE/'provenance.py').inspect(root,folder,r,c)
        report['actual_compilation_provenance_replayed']=True;report['receipt_sha256']=sha(receipt);report['mode']=r['mode']
        if producer_replay:
            result=load('producer_image_replay',runner).replay(root,receipt,firmware)
            need(result['passed'],'Supplemental producer full artifact replay');report['producer_archive_replay']=result
    if artifacts:
        obj,elf,binary=[Path(p).resolve(strict=True) for p in artifacts]
        report['independent_artifact_checks']=g.artifact_gate(c['E'](obj),c['E'](elf),binary,c)
        report['actual_new_artifacts_replayed']=True;report['actual_artifact_sha256']={k:sha(p) for k,p in zip(('object','ELF','BIN'),(obj,elf,binary))}
    return report
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,required=True);p.add_argument('--firmware',type=Path);p.add_argument('--receipt',type=Path);p.add_argument('--new-object',type=Path);p.add_argument('--new-elf',type=Path);p.add_argument('--new-bin',type=Path);p.add_argument('--producer-replay',action='store_true');p.add_argument('--output',type=Path);a=p.parse_args()
    explicit=[a.new_object,a.new_elf,a.new_bin];need(not any(explicit) or all(explicit),'All three explicit artifacts required');need(not(a.receipt and any(explicit)),'Select receipt or three explicit artifacts');need(not a.producer_replay or a.receipt,'Supplemental producer replay requires an actual archive receipt')
    r=inspect(a.project_root,a.firmware or firmware_default(a.project_root),a.receipt,explicit if all(explicit) else None,a.producer_replay)
    if a.output:
        out=a.output.resolve();out.relative_to(HERE);need(not out.exists(),'Create-only own review output');out.write_bytes((json.dumps(r,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(r if not a.output else {'passed':True,'output':str(a.output),'actual_new_artifacts_replayed':r['actual_new_artifacts_replayed'],'actual_compilation_provenance_replayed':r['actual_compilation_provenance_replayed']}))
if __name__=='__main__':main()
