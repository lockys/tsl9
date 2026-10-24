"""Reconstruct exact91-file parent manifest bytes without writing Git/files."""
from pathlib import Path
import hashlib,json,runpy
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS=ROOT/'experiments/tsl9-resident-providers/parent-manifest-v1.py'
K=ROOT/'experiments/tsl9-resident-providers/integration-v1.json'
P_SHA='82b3e7f87843a7d49567b05658b04f7c3aa392f871fc72014b0f6b48b11fbf4d'
K_SHA='f37da4624e5466a9a0958f70fe1150e0348c46c328156312fd96acae76bff862'
EXPECTED='332a072829f7fb88fdb1fb20dfe5439a0981bda87c55609f9ff6600b234ca243'
def need(ok,label):
    if not ok:raise ValueError(label)
def raw_parent():
    need(hashlib.sha256(PREVIOUS.read_bytes()).hexdigest()==P_SHA,'Pinned preceding derivation')
    need(hashlib.sha256(K.read_bytes()).hexdigest()==K_SHA,'Pinned main-family source extension')
    k=json.loads(K.read_bytes());raw=runpy.run_path(str(PREVIOUS))['raw_parent']()
    need(hashlib.sha256(raw).hexdigest()==k['previous_manifest_sha256'],'Exact90-file precursor')
    value=json.loads(raw);text=raw.decode('utf8')
    def block(item):return '\n'.join('    '+v for v in json.dumps(item,indent=2,ensure_ascii=False).splitlines())
    for group,key in [('files','new_file_entry'),('native_units','new_unit_entry')]:
        old=block(value[group][-1]);need(text.count(old)==1,'Unique exact insertion point')
        text=text.replace(old,old+',\n'+block(k[key]));value[group].append(k[key])
    data=text.encode('utf8')
    need(hashlib.sha256(data).hexdigest()==EXPECTED and json.loads(data)==value,'Exact91-file bytes and content')
    return data
if __name__=='__main__':
    raw=raw_parent()
    print(json.dumps(dict(passed=True,parent_sha256=EXPECTED,current_manifest_is_parent=(ROOT/'src/source-manifest.json').read_bytes()==raw,Git_history_written=False)))
