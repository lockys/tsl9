"""Exact79-file parent manifest derivation; no file or Git writes."""
from pathlib import Path
import hashlib
import json
import runpy
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS=ROOT/'experiments/tsl9-original-startup/parent-manifest-v1.py'
K=ROOT/'experiments/tsl9-original-startup/integration-v1.json'
P_SHA='1ba9b7f18ba74b67bb0ab4623788d2d1763604da7e13c3c83a4ffbb8a4243540'
K_SHA='350fee9924407b0f43b7244f96d2185146be7ae2259444414d39f9482ce9d042'
EXPECTED='c658a2044dc33033191d89732c53896e3332ffd991ec43de92f3e49f70bbe977'
def need(ok,why):
    if not ok:raise ValueError(why)
def raw_parent():
    need(hashlib.sha256(PREVIOUS.read_bytes()).hexdigest()==P_SHA,'Pinned previous manifest derivation')
    need(hashlib.sha256(K.read_bytes()).hexdigest()==K_SHA,'Pinned original startup extension')
    k=json.loads(K.read_bytes())
    raw=runpy.run_path(str(PREVIOUS))['raw_parent']()
    need(hashlib.sha256(raw).hexdigest()==k['previous_manifest_sha256'],'Exact78-file precursor')
    value=json.loads(raw);text=raw.decode('utf-8')
    def block(item):
        return '\n'.join('    '+s for s in json.dumps(item,indent=2,ensure_ascii=False).splitlines())
    for group,entry in [('files',k['new_file_entry']),('native_units',k['new_unit_entry'])]:
        last=block(value[group][-1])
        need(text.count(last)==1,'One exact insertion location')
        text=text.replace(last,last+',\n'+block(entry))
        value[group].append(entry)
    data=text.encode('utf-8')
    need(hashlib.sha256(data).hexdigest()==EXPECTED and json.loads(data)==value,'Exact79-file parent bytes and JSON')
    return data
if __name__=='__main__':
    raw=raw_parent()
    print(json.dumps(dict(passed=True,parent_sha256=EXPECTED,
        current_manifest_is_parent=(ROOT/'src/source-manifest.json').read_bytes()==raw,
        target_executed=False,Git_history_written=False)))
