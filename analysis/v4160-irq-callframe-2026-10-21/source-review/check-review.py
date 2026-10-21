#!/usr/bin/env python3
"""Read-only bindings of source inputs, peer seals and actual host receipts."""
import argparse
import hashlib
import json
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def sealed(path,expected):
    need(sha(path)==expected,'Seal identity')
    data=json.loads(path.read_text(encoding='utf-8'))
    for m in data.get('members',data.get('files',[])):
        q=(path.parent/m['path']).resolve(strict=True);q.relative_to(path.parent.resolve())
        need(sha(q)==m['sha256'],'Sealed member identity')
        if 'bytes' in m:need(q.stat().st_size==m['bytes'],'Sealed member size')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,required=True)
    a=p.parse_args();project=a.project_root.resolve(strict=True);root=Path(__file__).resolve().parent
    report=json.loads((root/'review.json').read_text(encoding='utf-8'))
    for m in report['component_inputs']:
        q=(project/m['path']).resolve(strict=True);q.relative_to(project)
        need(sha(q)==m['sha256'],'Frozen component dependency')
    for m in report['peer_seals']:
        choices=[root.parent.parent/n/m['subdirectory']/m['filename'] for n in m['scope_names']]
        choices=[q for q in choices if q.is_file()];need(len(choices)==1,'One peer evidence layout')
        sealed(choices[0],m['sha256'])
    modes=set();total=0
    for m in report['receipts']:
        q=(root/m['path']).resolve(strict=True);q.relative_to(root)
        need(sha(q)==m['sha256'],'Selected actual receipt')
        data=json.loads(q.read_text(encoding='utf-8'));modes.add(data['language'])
        need(data['passed'] and data['positive']['result']=={'passed':True,'groups':4,'cases':3820,'checks':138312},'Full independent fixture coverage')
        need(data['actual_source_translation_units']==2,'Actual main and helpers linked together')
        need(data['compiled_mutants_rejected']==30 and len(data['compiled_behavior_mutants'])==30,'Actually compiled behavior controls')
        need(all(x['result']['rejected'] for x in data['compiled_behavior_mutants'].values()),'Mutant assertion rejection')
        need(not data['native_bridge_or_register_proof'],'No promotion of host results to target proof')
        total+=data['compiled_mutants_rejected']
    need(modes=={'c','cpp'},'C11 and C++17 receipts')
    if (root/'seal.json').is_file():sealed(root/'seal.json',sha(root/'seal.json'))
    print(json.dumps({'passed':True,'host_modes':2,'compiled_behavior_mutants_rejected':total,'native_bridge_or_register_proved':False,'target_execution':False,'ISA_emulation':False,'hardware':False,'OTA_ready':False},sort_keys=True))
if __name__=='__main__':main()
