"""Reconstruct exact 115-file parent manifest without filesystem or Git mutation."""
from pathlib import Path
import hashlib,json,runpy
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS=ROOT/'experiments/tsl9-peripheral-initializer/parent-manifest-v1.py'
K=ROOT/'experiments/tsl9-peripheral-initializer/source-extension-v1.json'
P_SHA='4f83a5eb72392e2fa6100835abdb8dd0cd286fb4e353a87d4820f631efab8207'
K_SHA='97a25976804a75188acad8499a13a2acacde9fe951f86147d61e885f76b5d9cd'
EXPECTED='b44b017c8b10b01573a341376b0e56e9252cf574b677a210e2c98db70ba14379'
def need(ok,label):
    if not ok:raise ValueError(label)
def raw_parent():
    need(hashlib.sha256(PREVIOUS.read_bytes()).hexdigest()==P_SHA,'Pinned previous derivation')
    need(hashlib.sha256(K.read_bytes()).hexdigest()==K_SHA,'Pinned previous source extension')
    k=json.loads(K.read_bytes());raw=runpy.run_path(str(PREVIOUS))['raw_parent']()
    need(hashlib.sha256(raw).hexdigest()==k['previous_manifest_sha256'],'Exact 114-file precursor')
    value=json.loads(raw);text=raw.decode('utf8')
    def block(v):return '\n'.join('    '+l for l in json.dumps(v,indent=2,ensure_ascii=False).splitlines())
    for group,key in [('files','new_file_entry'),('native_units','new_unit_entry')]:
        old=block(value[group][-1]);need(text.count(old)==1,'Exact unique insertion point')
        text=text.replace(old,old+',\n'+block(k[key]));value[group].append(k[key])
    result=text.encode('utf8')
    need(hashlib.sha256(result).hexdigest()==EXPECTED and json.loads(result)==value,'Exact original 115-file bytes')
    return result
if __name__=='__main__':
    print(json.dumps(dict(passed=bool(raw_parent()),parent_sha256=EXPECTED,files_written=False)))
