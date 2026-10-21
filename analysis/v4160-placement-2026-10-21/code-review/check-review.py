#!/usr/bin/env python3
"""Read-only evidence binding; does not rerun compilers, firmware or host tests."""
import argparse
import hashlib
import json
from pathlib import Path

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def need(value,message):
    if not value:raise ValueError(message)
def verify_seal(path,expected):
    need(sha(path)==expected,'Exact peer seal identity')
    seal=json.loads(path.read_text(encoding='utf-8'))
    for member in seal.get('members',seal.get('files',[])):
        p=(path.parent/member['path']).resolve(strict=True)
        p.relative_to(path.parent.resolve())
        need(sha(p)==member['sha256'],'Exact peer member identity')
        if 'bytes' in member:need(p.stat().st_size==member['bytes'],'Exact peer member size')
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',type=Path,required=True)
    p.add_argument('--review-root',type=Path,default=Path(__file__).resolve().parent)
    a=p.parse_args();project=a.project_root.resolve(strict=True);root=a.review_root.resolve(strict=True)
    review=json.loads((root/'review.json').read_text(encoding='utf-8'))
    for item in review['component_inputs']:
        target=(project/item['path']).resolve(strict=True);target.relative_to(project)
        need(sha(target)==item['sha256'],'Frozen component input identity')
    verify_seal(root.parent/'source-review/final-audit.json',review['placement_source_seal_sha256'])
    verify_seal(root.parent/'abi-review/seal.json',review['old_component_ABI_counterevidence_seal_sha256'])
    oldroots=[root.parent.parent/name/'source' for name in ('tsl9-v4160-interrupt-init-2026-10-21','v4160-interrupt-init-2026-10-21')]
    oldroots=[x for x in oldroots if (x/'final-audit.json').is_file()]
    need(len(oldroots)==1,'One known immutable original IRQ source layout')
    verify_seal(oldroots[0]/'final-audit.json',review['original_source_seal_sha256'])
    total=0
    for item in review['independent_receipts']:
        path=(root/item['path']).resolve(strict=True);path.relative_to(root)
        need(sha(path)==item['sha256'],'Independent selected receipt identity')
        receipt=json.loads(path.read_text(encoding='utf-8'))
        need(receipt['passed'] and receipt['positive']['result']=={'passed':True,'groups':4,'cases':3820,'checks':138312},'Independent complete coverage')
        need(receipt['compiled_mutants_rejected']==18,'Actual compiled mutation count')
        total+=receipt['compiled_mutants_rejected']
    for item in review['parent_receipts']:
        path=(root/item['path']).resolve(strict=True);path.relative_to(root)
        need(sha(path)==item['sha256'],'Parent selected receipt identity')
        receipt=json.loads(path.read_text(encoding='utf-8'))
        need(receipt['passed'] and receipt['tests']=={'passed':True,'groups':4,'cases':9184,'checks':246384},'Parent full host coverage')
        need(receipt['source_proof_checked'],'Parent source proof replay required')
        need(not receipt['native_registers_checked'],'No host-to-native proof promotion')
    print(json.dumps({'passed':True,'independent_modes':2,'compiled_behavior_mutants_rejected':total,
                      'parent_full_host_modes':2,'actual_native_A2_A3_proved':False,
                      'target_execution':False,'ISA_emulation':False,'hardware':False,'OTA_ready':False},sort_keys=True))
if __name__=='__main__':main()
