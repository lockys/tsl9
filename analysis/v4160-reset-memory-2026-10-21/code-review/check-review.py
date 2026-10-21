#!/usr/bin/env python3
"""Read-only binding of independent review receipts; no test rerun."""
import argparse
import hashlib
import json
from pathlib import Path

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check_record(root, item):
    path = (root/item['path']).resolve(strict=True)
    path.relative_to(root)
    if sha(path) != item['sha256']:
        raise ValueError('Bound review artifact mismatch: '+str(path))
    return path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',type=Path,required=True)
    p.add_argument('--review-root',type=Path,default=Path(__file__).resolve().parent)
    a=p.parse_args()
    project=a.project_root.resolve(strict=True)
    root=a.review_root.resolve(strict=True)
    record=json.loads((root/'review.json').read_text(encoding='utf-8'))
    source=root.parent/'source-review'
    if sha(source/'final-audit.json')!=record['source_seal_sha256']:
        raise ValueError('Original source review seal mismatch')
    for member in json.loads((source/'final-audit.json').read_text(encoding='utf-8'))['members']:
        path=(source/member['path']).resolve(strict=True)
        path.relative_to(source.resolve())
        if path.stat().st_size!=member['bytes'] or sha(path)!=member['sha256']:
            raise ValueError('Original source review member mismatch')
    for item in record['component_inputs']:
        check_record(project,item)
    count=0
    for item in record['independent_receipts']:
        receipt=check_record(root,item)
        result=json.loads(receipt.read_text(encoding='utf-8'))
        if not result['passed'] or result['compiled_mutants_rejected']!=11 or result['positive']['result']!={'passed':True,'groups':5,'cases':538,'checks':193964}:
            raise ValueError('Unexpected independent test coverage')
        count+=result['compiled_mutants_rejected']
    for item in record.get('parent_receipts',[]):
        path=check_record(root,item)
        result=json.loads(path.read_text(encoding='utf-8'))
        if not result.get('passed') or result.get('tests')!={'passed':True,'groups':5,'cases':338,'checks':133601}:
            raise ValueError('Unexpected parent host coverage')
    print(json.dumps({'passed':True,'independent_modes':len(record['independent_receipts']),
                      'compiled_behavior_mutants_rejected':count,'source_component_identity_bound':True,
                      'target_execution':False,'hardware':False,'OTA_ready':False},sort_keys=True))

if __name__=='__main__':
    main()
