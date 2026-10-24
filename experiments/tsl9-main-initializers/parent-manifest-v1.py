"""Reconstruct exact 113-file parent manifest without filesystem or Git mutation."""
from pathlib import Path
import hashlib,json,runpy
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS=ROOT/'experiments/tsl9-ota-finalizers/parent-manifest-v1.py'
K=ROOT/'experiments/tsl9-ota-finalizers/source-extension-v1.json'
P_SHA='8ca4b1b76a4517762130548ed32dc251e54813e24b50f90cb55ad81a7ee54fe0'
K_SHA='888dc0da5355d14754b04b43034ea058e9b22f10f0b962756604d628446c88ce'
EXPECTED='2e664861dd1b354943e6fa0034a8b34193dd9e6e7dbeab3fae1077099d745cc9'
def need(ok,label):
    if not ok:raise ValueError(label)
def raw_parent():
    need(hashlib.sha256(PREVIOUS.read_bytes()).hexdigest()==P_SHA,'Pinned previous derivation')
    need(hashlib.sha256(K.read_bytes()).hexdigest()==K_SHA,'Pinned previous source extension')
    k=json.loads(K.read_bytes());raw=runpy.run_path(str(PREVIOUS))['raw_parent']()
    need(hashlib.sha256(raw).hexdigest()==k['previous_manifest_sha256'],'Exact 112-file precursor')
    value=json.loads(raw);text=raw.decode('utf8')
    def block(v):return '\n'.join('    '+l for l in json.dumps(v,indent=2,ensure_ascii=False).splitlines())
    for group,key in [('files','new_file_entry'),('native_units','new_unit_entry')]:
        old=block(value[group][-1]);need(text.count(old)==1,'Exact unique insertion point')
        text=text.replace(old,old+',\n'+block(k[key]));value[group].append(k[key])
    result=text.encode('utf8')
    need(hashlib.sha256(result).hexdigest()==EXPECTED and json.loads(result)==value,'Exact original 113-file bytes')
    return result
if __name__=='__main__':
    print(json.dumps(dict(passed=bool(raw_parent()),parent_sha256=EXPECTED,files_written=False)))
