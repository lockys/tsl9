#!/usr/bin/env python3
"""Read-only source/receipt binding; no compiler or target execution."""
import argparse
import hashlib
import json
from pathlib import Path

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def need(value,message):
    if not value:raise ValueError(message)
def sealed(path,expected):
    need(sha(path)==expected,'Peer seal identity')
    value=json.loads(path.read_text(encoding='utf-8'))
    for item in value.get('members',value.get('files',[])):
        p=(path.parent/item['path']).resolve(strict=True);p.relative_to(path.parent.resolve())
        need(sha(p)==item['sha256'],'Peer member hash')
        if 'bytes' in item:need(p.stat().st_size==item['bytes'],'Peer member size')
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root',type=Path,required=True)
    args=parser.parse_args();project=args.project_root.resolve(strict=True);root=Path(__file__).resolve().parent
    report=json.loads((root/'review.json').read_text(encoding='utf-8'))
    for item in report['component_inputs']:
        target=(project/item['path']).resolve(strict=True);target.relative_to(project)
        need(sha(target)==item['sha256'],'Frozen component input hash')
    for item in report['peer_seals']:
        choices=[root.parent.parent/name/item['subdirectory']/item['filename'] for name in item['scope_names']]
        choices=[p for p in choices if p.is_file()];need(len(choices)==1,'One known peer evidence layout')
        sealed(choices[0],item['sha256'])
    total=0
    for item in report['receipts']:
        path=(root/item['path']).resolve(strict=True);path.relative_to(root)
        need(sha(path)==item['sha256'],'Selected receipt hash')
        value=json.loads(path.read_text(encoding='utf-8'))
        need(value['passed'] and value['positive']['result']=={'passed':True,'groups':4,'cases':3820,'checks':138312},'Full independent coverage')
        need(value['compiled_mutants_rejected']==22 and len(value['compiled_behavior_mutants'])==22,'Actually compiled behavior controls')
        need(not value['native_bridge_or_register_proof'],'No host-to-native promotion')
        total+=value['compiled_mutants_rejected']
    print(json.dumps({'passed':True,'host_modes':2,'compiled_behavior_mutants_rejected':total,
                      'native_register_or_bridge_proved':False,'target_execution':False,
                      'ISA_emulation':False,'hardware':False,'OTA_ready':False},sort_keys=True))
if __name__=='__main__':main()
