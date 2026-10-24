"""Exact82-file retained parent manifest; no file or Git writes."""
from pathlib import Path
import hashlib
import json
import runpy
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS=ROOT/'experiments/tsl9-ecall-restore/parent-manifest-v1.py'
K=ROOT/'experiments/tsl9-ecall-restore/integration-v1.json'
P_SHA='f15e7938fcf0deea744ea0d43deaec8c2e87e12c75d527225a446c7ba97e6e0d'
K_SHA='d6a092c22540aafd17d42e9601eafd34967aa26c1339ed7d78f2e0e7ae613dae'
EXPECTED='9660c145ff144816d44e3772ad854349cae85acd91263c1a71dc4ec8f90a730e'
def need(ok,message):
    if not ok:raise ValueError(message)
def raw_parent():
    need(hashlib.sha256(PREVIOUS.read_bytes()).hexdigest()==P_SHA,'Pinned previous exact derivation')
    need(hashlib.sha256(K.read_bytes()).hexdigest()==K_SHA,'Pinned ECALL source extension')
    k=json.loads(K.read_bytes())
    raw=runpy.run_path(str(PREVIOUS))['raw_parent']()
    need(hashlib.sha256(raw).hexdigest()==k['previous_manifest_sha256'],'Exact81-file precursor')
    value=json.loads(raw);text=raw.decode('utf-8')
    def block(item):
        return '\n'.join('    '+s for s in json.dumps(item,indent=2,ensure_ascii=False).splitlines())
    for group,entry in [('files',k['new_file_entry']),('native_units',k['new_unit_entry'])]:
        old=block(value[group][-1])
        need(text.count(old)==1,'One exact insertion location')
        text=text.replace(old,old+',\n'+block(entry));value[group].append(entry)
    data=text.encode('utf-8')
    need(hashlib.sha256(data).hexdigest()==EXPECTED and json.loads(data)==value,'Exact82-file bytes and JSON')
    return data
if __name__=='__main__':
    raw=raw_parent()
    print(json.dumps(dict(passed=True,parent_sha256=EXPECTED,
        current_manifest_is_parent=(ROOT/'src/source-manifest.json').read_bytes()==raw,
        target_executed=False,Git_history_written=False)))
