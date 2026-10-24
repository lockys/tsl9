"""Exact81-file retained parent manifest; no file or Git writes."""
from pathlib import Path
import hashlib
import json
import runpy
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS=ROOT/'experiments/tsl9-lle-irq/parent-manifest-v1.py'
K=ROOT/'experiments/tsl9-lle-irq/integration-v1.json'
P_SHA='d06d7b07e87e284dbba371cfe6fc794abdebfcf456a4ccefd805a42fd090448a'
K_SHA='6c9ea5595bcb88816044a8ba566b7bc961d0b51a6fd25183d3ea828f816c2150'
EXPECTED='21b963751363a015497de279b2e2561a62b8a6c69a1b72f8227fcf0df2223a81'
def need(ok,message):
    if not ok:raise ValueError(message)
def raw_parent():
    need(hashlib.sha256(PREVIOUS.read_bytes()).hexdigest()==P_SHA,'Pinned previous exact derivation')
    need(hashlib.sha256(K.read_bytes()).hexdigest()==K_SHA,'Pinned LLE source extension')
    k=json.loads(K.read_bytes())
    raw=runpy.run_path(str(PREVIOUS))['raw_parent']()
    need(hashlib.sha256(raw).hexdigest()==k['previous_manifest_sha256'],'Exact80-file precursor')
    value=json.loads(raw);text=raw.decode('utf-8')
    def block(item):
        return '\n'.join('    '+s for s in json.dumps(item,indent=2,ensure_ascii=False).splitlines())
    for group,entry in [('files',k['new_file_entry']),('native_units',k['new_unit_entry'])]:
        old=block(value[group][-1])
        need(text.count(old)==1,'One exact insertion location')
        text=text.replace(old,old+',\n'+block(entry));value[group].append(entry)
    data=text.encode('utf-8')
    need(hashlib.sha256(data).hexdigest()==EXPECTED and json.loads(data)==value,'Exact81-file bytes and JSON')
    return data
if __name__=='__main__':
    raw=raw_parent()
    print(json.dumps(dict(passed=True,parent_sha256=EXPECTED,
        current_manifest_is_parent=(ROOT/'src/source-manifest.json').read_bytes()==raw,
        target_executed=False,Git_history_written=False)))
