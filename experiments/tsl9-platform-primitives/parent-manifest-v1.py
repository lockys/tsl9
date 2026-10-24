"""Reconstruct exact 117-file parent manifest without filesystem or Git mutation."""
from pathlib import Path
import hashlib,json,runpy
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS=ROOT/'experiments/tsl9-main-services/parent-manifest-v1.py'
K=ROOT/'experiments/tsl9-main-services/source-extension-v1.json'
P_SHA='57d9ed54307fe1fd948ef386e851687800a9f981a0f8fb91f0395455b80dad5b'
K_SHA='04b95fd56b962c1692c1799b3175d0123375e521cf2f2074cf2600763ef58127'
EXPECTED='d4f7a9448313199a6ed04d1a7e8836387adf94e6d532bc3ed5639ce4a48ac13a'
def need(ok,label):
    if not ok:raise ValueError(label)
def raw_parent():
    need(hashlib.sha256(PREVIOUS.read_bytes()).hexdigest()==P_SHA,'Pinned previous derivation')
    need(hashlib.sha256(K.read_bytes()).hexdigest()==K_SHA,'Pinned previous source extension')
    k=json.loads(K.read_bytes());raw=runpy.run_path(str(PREVIOUS))['raw_parent']()
    need(hashlib.sha256(raw).hexdigest()==k['previous_manifest_sha256'],'Exact 116-file precursor')
    value=json.loads(raw);text=raw.decode('utf8')
    def block(v):return '\n'.join('    '+l for l in json.dumps(v,indent=2,ensure_ascii=False).splitlines())
    for group,key in [('files','new_file_entry'),('native_units','new_unit_entry')]:
        old=block(value[group][-1]);need(text.count(old)==1,'Exact unique insertion point')
        text=text.replace(old,old+',\n'+block(k[key]));value[group].append(k[key])
    result=text.encode('utf8')
    need(hashlib.sha256(result).hexdigest()==EXPECTED and json.loads(result)==value,'Exact original 117-file bytes')
    return result
if __name__=='__main__':
    print(json.dumps(dict(passed=bool(raw_parent()),parent_sha256=EXPECTED,files_written=False)))
