"""Reconstruct exact93-file parent manifest bytes without writing Git/files."""
from pathlib import Path
import hashlib,json,runpy
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS=ROOT/'experiments/tsl9-rf-completion/parent-manifest-v1.py'
K=ROOT/'experiments/tsl9-rf-completion/integration-v1.json'
P_SHA='e83aa3eecdf362e4f5138f9c6ecb9ce8eff2663bf4c916d07c114595d68ae5a3'
K_SHA='63891290ad4f1d600e4e1a339a009083fe1f3035390a35bb66ff57a1c471291b'
EXPECTED='11d3b05b74505b320c810f4164a7bafd3585d01ffcb3753c914365cdc61065aa'
def need(ok,label):
    if not ok:raise ValueError(label)
def raw_parent():
    need(hashlib.sha256(PREVIOUS.read_bytes()).hexdigest()==P_SHA,'Pinned preceding derivation')
    need(hashlib.sha256(K.read_bytes()).hexdigest()==K_SHA,'Pinned main-family source extension')
    k=json.loads(K.read_bytes());raw=runpy.run_path(str(PREVIOUS))['raw_parent']()
    need(hashlib.sha256(raw).hexdigest()==k['previous_manifest_sha256'],'Exact92-file precursor')
    value=json.loads(raw);text=raw.decode('utf8')
    def block(item):return '\n'.join('    '+v for v in json.dumps(item,indent=2,ensure_ascii=False).splitlines())
    for group,key in [('files','new_file_entry'),('native_units','new_unit_entry')]:
        old=block(value[group][-1]);need(text.count(old)==1,'Unique exact insertion point')
        text=text.replace(old,old+',\n'+block(k[key]));value[group].append(k[key])
    data=text.encode('utf8')
    need(hashlib.sha256(data).hexdigest()==EXPECTED and json.loads(data)==value,'Exact93-file bytes and content')
    return data
if __name__=='__main__':
    raw=raw_parent()
    print(json.dumps(dict(passed=True,parent_sha256=EXPECTED,current_manifest_is_parent=(ROOT/'src/source-manifest.json').read_bytes()==raw,Git_history_written=False)))
