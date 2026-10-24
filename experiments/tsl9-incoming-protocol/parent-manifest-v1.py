"""Reconstruct exact 109-file parent manifest without filesystem or Git mutation."""
from pathlib import Path
import hashlib,json,runpy
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS=ROOT/'experiments/tsl9-runtime-callbacks/parent-manifest-v1.py'
K=ROOT/'experiments/tsl9-runtime-callbacks/source-extension-v1.json'
P_SHA='60b8a870fc6784dc3fe1c80dfa1c22a4c3e8c2ecc25c3b9c196a384c8bc98d4d'
K_SHA='c3d1e304aa5c7f3999339cc6fa22d86e30345fd2860268dd4802d54a1cbcaa29'
EXPECTED='5cc4571d2cc01afdbd0c681efdd2426ca15124ca13744ae2cafce7eba10fa662'
def need(ok,label):
    if not ok:raise ValueError(label)
def raw_parent():
    need(hashlib.sha256(PREVIOUS.read_bytes()).hexdigest()==P_SHA,'Pinned previous derivation')
    need(hashlib.sha256(K.read_bytes()).hexdigest()==K_SHA,'Pinned previous source extension')
    k=json.loads(K.read_bytes());raw=runpy.run_path(str(PREVIOUS))['raw_parent']()
    need(hashlib.sha256(raw).hexdigest()==k['previous_manifest_sha256'],'Exact 108-file precursor')
    value=json.loads(raw);text=raw.decode('utf8')
    def block(v):return '\n'.join('    '+l for l in json.dumps(v,indent=2,ensure_ascii=False).splitlines())
    for group,key in [('files','new_file_entry'),('native_units','new_unit_entry')]:
        old=block(value[group][-1]);need(text.count(old)==1,'Exact unique insertion point')
        text=text.replace(old,old+',\n'+block(k[key]));value[group].append(k[key])
    result=text.encode('utf8')
    need(hashlib.sha256(result).hexdigest()==EXPECTED and json.loads(result)==value,'Exact original 109-file bytes')
    return result
if __name__=='__main__':
    print(json.dumps(dict(passed=bool(raw_parent()),parent_sha256=EXPECTED,files_written=False)))
