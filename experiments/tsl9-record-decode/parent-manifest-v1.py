"""Reconstruct exact94-file parent manifest bytes without writing Git/files."""
from pathlib import Path
import hashlib,json,runpy
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS=ROOT/'experiments/tsl9-record-consumer/parent-manifest-v1.py'
K=ROOT/'experiments/tsl9-record-consumer/integration-v1.json'
P_SHA='b12b30968663b655b6806443be67f6d57c421692ea053253b2dd20d48e828806'
K_SHA='764c7c63cd45dee4d3211721cdff9c680f86f5ce26de93aa3b0a4b98f4dcef31'
EXPECTED='53229c00474e9f5994da78bd9fb4d9ad85481fe01f0767f88d039356a6048674'
def need(ok,label):
    if not ok:raise ValueError(label)
def raw_parent():
    need(hashlib.sha256(PREVIOUS.read_bytes()).hexdigest()==P_SHA,'Pinned preceding derivation')
    need(hashlib.sha256(K.read_bytes()).hexdigest()==K_SHA,'Pinned main-family source extension')
    k=json.loads(K.read_bytes());raw=runpy.run_path(str(PREVIOUS))['raw_parent']()
    need(hashlib.sha256(raw).hexdigest()==k['previous_manifest_sha256'],'Exact93-file precursor')
    value=json.loads(raw);text=raw.decode('utf8')
    def block(item):return '\n'.join('    '+v for v in json.dumps(item,indent=2,ensure_ascii=False).splitlines())
    for group,key in [('files','new_file_entry'),('native_units','new_unit_entry')]:
        old=block(value[group][-1]);need(text.count(old)==1,'Unique exact insertion point')
        text=text.replace(old,old+',\n'+block(k[key]));value[group].append(k[key])
    data=text.encode('utf8')
    need(hashlib.sha256(data).hexdigest()==EXPECTED and json.loads(data)==value,'Exact94-file bytes and content')
    return data
if __name__=='__main__':
    raw=raw_parent()
    print(json.dumps(dict(passed=True,parent_sha256=EXPECTED,current_manifest_is_parent=(ROOT/'src/source-manifest.json').read_bytes()==raw,Git_history_written=False)))
