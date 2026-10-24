"""Reconstruct exact87-file parent manifest bytes without writing Git/files."""
from pathlib import Path
import hashlib,json,runpy
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS=ROOT/'experiments/tsl9-callback-family/parent-manifest-v1.py'
K=ROOT/'experiments/tsl9-callback-family/integration-v1.json'
P_SHA='a15328c11019013ce10911d8d83a3df1ff37264b272dafd8a302e389a22adeec'
K_SHA='22b56bd3ea808c46128fda704362fe2bd5ffee99068c44d2ae4a8ebd268ba046'
EXPECTED='6e0a3981137c8cfe1395f773fbd73e02f64efee8031ca2eb913805a760954a63'
def need(ok,label):
    if not ok:raise ValueError(label)
def raw_parent():
    need(hashlib.sha256(PREVIOUS.read_bytes()).hexdigest()==P_SHA,'Pinned preceding derivation')
    need(hashlib.sha256(K.read_bytes()).hexdigest()==K_SHA,'Pinned main-family source extension')
    k=json.loads(K.read_bytes());raw=runpy.run_path(str(PREVIOUS))['raw_parent']()
    need(hashlib.sha256(raw).hexdigest()==k['previous_manifest_sha256'],'Exact86-file precursor')
    value=json.loads(raw);text=raw.decode('utf8')
    def block(item):return '\n'.join('    '+v for v in json.dumps(item,indent=2,ensure_ascii=False).splitlines())
    for group,key in [('files','new_file_entry'),('native_units','new_unit_entry')]:
        old=block(value[group][-1]);need(text.count(old)==1,'Unique exact insertion point')
        text=text.replace(old,old+',\n'+block(k[key]));value[group].append(k[key])
    data=text.encode('utf8')
    need(hashlib.sha256(data).hexdigest()==EXPECTED and json.loads(data)==value,'Exact87-file bytes and content')
    return data
if __name__=='__main__':
    raw=raw_parent()
    print(json.dumps(dict(passed=True,parent_sha256=EXPECTED,current_manifest_is_parent=(ROOT/'src/source-manifest.json').read_bytes()==raw,Git_history_written=False)))
