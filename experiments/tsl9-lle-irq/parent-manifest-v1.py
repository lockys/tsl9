"""Exact80-file retained parent manifest; no file or Git writes."""
from pathlib import Path
import hashlib
import json
import runpy
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS=ROOT/'experiments/tsl9-original-vectors/parent-manifest-v1.py'
K=ROOT/'experiments/tsl9-original-vectors/integration-v1.json'
P_SHA='80987793ce384cfdb752beda839c1e356d32ee87e9f1a359b0be97c44c6a6717'
K_SHA='b0ab08793c10624c5c9654a2c609a5194d33574b3ca98ae4c12fb722b5118d9c'
EXPECTED='22b04189ed25a36c9f196b6080c0b7309525363f34beed0e7c072f7783a18ed8'
def need(ok,message):
    if not ok:raise ValueError(message)
def raw_parent():
    need(hashlib.sha256(PREVIOUS.read_bytes()).hexdigest()==P_SHA,'Pinned prior exact derivation')
    need(hashlib.sha256(K.read_bytes()).hexdigest()==K_SHA,'Pinned native-vector registration')
    k=json.loads(K.read_bytes())
    raw=runpy.run_path(str(PREVIOUS))['raw_parent']()
    need(hashlib.sha256(raw).hexdigest()==k['previous_manifest_sha256'],'Exact79-file precursor')
    value=json.loads(raw);text=raw.decode('utf-8')
    def block(item):
        return '\n'.join('    '+s for s in json.dumps(item,indent=2,ensure_ascii=False).splitlines())
    old=block(value['files'][-1])
    need(text.count(old)==1,'One exact original last-file location')
    text=text.replace(old,old+',\n'+block(k['new_file_entry']))
    value['files'].append(k['new_file_entry'])
    marker='  "legacy_groups": ['
    need(text.count(marker)==1 and 'native_data_units'not in value,'One exact data-unit insertion')
    registration='\n'.join(json.dumps({'native_data_units':[k['new_data_unit']]},
                                      indent=2,ensure_ascii=False).splitlines()[1:-1])
    text=text.replace(marker,registration+',\n'+marker)
    value['native_data_units']=[k['new_data_unit']]
    data=text.encode('utf-8')
    need(hashlib.sha256(data).hexdigest()==EXPECTED and json.loads(data)==value,'Exact80-file parent bytes and JSON')
    return data
if __name__=='__main__':
    raw=raw_parent()
    print(json.dumps(dict(passed=True,parent_sha256=EXPECTED,
        current_manifest_is_parent=(ROOT/'src/source-manifest.json').read_bytes()==raw,
        target_executed=False,Git_history_written=False)))
