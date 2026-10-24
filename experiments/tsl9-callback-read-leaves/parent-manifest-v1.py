"""Reconstruct exact 101-file parent manifest without filesystem or Git mutation."""
from pathlib import Path
import hashlib,json,runpy
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS=ROOT/'experiments/tsl9-irq-initializer/parent-manifest-v1.py'
K=ROOT/'experiments/tsl9-irq-initializer/source-extension-v1.json'
P_SHA='26b13e5b921f60eda46c65a94e179c1672634535440fe09e857d10a45c0ec622'
K_SHA='076b382b49469c7c35378135d0fa9e610551dd03bb7119bc03e8f4256cc82881'
EXPECTED='f538d7bf2d0036121939194d8f093920546a3767b7eec63ec5e7c8465a9c9389'
def need(ok,label):
    if not ok:raise ValueError(label)
def raw_parent():
    need(hashlib.sha256(PREVIOUS.read_bytes()).hexdigest()==P_SHA,'Pinned previous derivation')
    need(hashlib.sha256(K.read_bytes()).hexdigest()==K_SHA,'Pinned previous source extension')
    k=json.loads(K.read_bytes());raw=runpy.run_path(str(PREVIOUS))['raw_parent']()
    need(hashlib.sha256(raw).hexdigest()==k['previous_manifest_sha256'],'Exact 100-file precursor')
    value=json.loads(raw);text=raw.decode('utf8')
    def block(v):return '\n'.join('    '+l for l in json.dumps(v,indent=2,ensure_ascii=False).splitlines())
    for group,key in [('files','new_file_entry'),('native_units','new_unit_entry')]:
        old=block(value[group][-1]);need(text.count(old)==1,'Exact unique insertion point')
        text=text.replace(old,old+',\n'+block(k[key]));value[group].append(k[key])
    result=text.encode('utf8')
    need(hashlib.sha256(result).hexdigest()==EXPECTED and json.loads(result)==value,'Exact original 101-file bytes')
    return result
if __name__=='__main__':
    print(json.dumps(dict(passed=bool(raw_parent()),parent_sha256=EXPECTED,files_written=False)))
