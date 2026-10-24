"""Reconstruct the exact retained77-file parent manifest; metadata only."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]
K=ROOT/'experiments/tsl9-state-access/integration-v1.json'
EXPECTED_K_SHA='ab5d51502cbea67103b6ae1abd6a5bd9f92bb3a59738cd5193e87250179ba3bc'
EXPECTED_PARENT_SHA='2c26c3efcbcf916dc40fc090919c6417d9c80612832dc1ade1b8bf2ba68e5f80'

def need(ok,why):
    if not ok:raise ValueError(why)

def raw_parent():
    need(hashlib.sha256(K.read_bytes()).hexdigest()==EXPECTED_K_SHA,'Frozen parent source-extension contract')
    k=json.loads(K.read_bytes())
    p=subprocess.run(['git','show',k['base_commit']+':src/source-manifest.json'],
                     cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
    need(p.returncode==0,'Retained original Git manifest')
    need(hashlib.sha256(p.stdout).hexdigest()==k['previous_manifest_sha256'],'Exact original76-file bytes')
    value=json.loads(p.stdout);raw=p.stdout.decode('utf-8')
    def block(item):
        return '\n'.join('    '+s for s in json.dumps(item,indent=2,ensure_ascii=False).splitlines())
    for group,entry in [('files',k['new_file_entry']),('native_units',k['new_unit_entry'])]:
        last=block(value[group][-1])
        need(raw.count(last)==1,'One exact recorded native insertion context')
        raw=raw.replace(last,last+',\n'+block(entry))
        value[group].append(entry)
    encoded=raw.encode('utf-8')
    need(hashlib.sha256(encoded).hexdigest()==EXPECTED_PARENT_SHA,'Exact pre-existing77-file parent bytes')
    need(json.loads(encoded)==value,'Complete parent JSON construction')
    return encoded

if __name__=='__main__':
    raw=raw_parent();d=json.loads(raw)
    current=ROOT/'src/source-manifest.json'
    print(json.dumps(dict(passed=True,parent_sha256=EXPECTED_PARENT_SHA,C_H_files=len(d['files']),
                         native_units=len(d['native_units']),current_manifest_is_parent=current.read_bytes()==raw,
                         Git_history_written=False,target_executed=False)))
