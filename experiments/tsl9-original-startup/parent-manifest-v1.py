"""Exact retained78-file parent manifest; no target execution or file writes."""
import hashlib
import json
import runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS=ROOT/'experiments/tsl9-state-events/parent-manifest-v1.py'
K=ROOT/'experiments/tsl9-state-events/integration-v1.json'
EXPECTED_PREVIOUS_SHA='bac80a840dfa03d439dcad38f594a5ae45a2adc8b1fd8e0b8a29f2642d0a8b49'
EXPECTED_K_SHA='6cbb284d402c072b62587def58ccb0acf5ed95ccd0079158933dc51ca730acae'
EXPECTED_PARENT_SHA='4f0cf189c5ee343e6230dca804c8cf2719afe72905d0104ec80731ace7cb41fa'

def need(ok,why):
    if not ok:raise ValueError(why)

def raw_parent():
    need(hashlib.sha256(PREVIOUS.read_bytes()).hexdigest()==EXPECTED_PREVIOUS_SHA,'Pinned previous exact manifest derivation')
    need(hashlib.sha256(K.read_bytes()).hexdigest()==EXPECTED_K_SHA,'Pinned state-events extension contract')
    k=json.loads(K.read_bytes());raw=runpy.run_path(str(PREVIOUS))['raw_parent']()
    need(hashlib.sha256(raw).hexdigest()==k['previous_manifest_sha256'],'Exact retained77-file predecessor')
    value=json.loads(raw);text=raw.decode('utf-8')
    def block(item):
        return '\n'.join('    '+x for x in json.dumps(item,indent=2,ensure_ascii=False).splitlines())
    for group,entry in [('files',k['new_file_entry']),('native_units',k['new_unit_entry'])]:
        last=block(value[group][-1]);need(text.count(last)==1,'One exact recorded insertion')
        text=text.replace(last,last+',\n'+block(entry));value[group].append(entry)
    data=text.encode('utf-8')
    need(hashlib.sha256(data).hexdigest()==EXPECTED_PARENT_SHA,'Exact pre-existing78-file parent bytes')
    need(json.loads(data)==value,'Complete byte-derived parent JSON')
    return data

if __name__=='__main__':
    data=raw_parent();value=json.loads(data)
    print(json.dumps(dict(passed=True,C_H_files=len(value['files']),native_units=len(value['native_units']),
                         parent_sha256=EXPECTED_PARENT_SHA,current_manifest_is_parent=(ROOT/'src/source-manifest.json').read_bytes()==data,
                         target_executed=False,Git_history_written=False)))
