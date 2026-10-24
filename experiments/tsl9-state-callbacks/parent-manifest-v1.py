"""Reconstruct exact 95-file parent manifest without modifying files or Git."""
from pathlib import Path
import hashlib,json,runpy
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS=ROOT/'experiments/tsl9-record-decode/parent-manifest-v1.py'
K=ROOT/'experiments/tsl9-record-decode/integration-v1.json'
P_SHA='618e1e3e0c45f8cdeb20055a7770b5c8888525966579106a118bc1fc7797de71'
K_SHA='f06517800e8499a6350d4fe268a763f42533c6c75b30a9a7988771c5141a7ff1'
EXPECTED='ec8ef18a817bd23595caaeb06578fbd44e62361151c94054a344dcdfe90ac4da'

def need(ok,label):
    if not ok:raise ValueError(label)
def raw_parent():
    need(hashlib.sha256(PREVIOUS.read_bytes()).hexdigest()==P_SHA,'Pinned preceding derivation')
    need(hashlib.sha256(K.read_bytes()).hexdigest()==K_SHA,'Pinned record-decode source extension')
    k=json.loads(K.read_bytes());raw=runpy.run_path(str(PREVIOUS))['raw_parent']()
    need(hashlib.sha256(raw).hexdigest()==k['previous_manifest_sha256'],'Exact 94-file precursor')
    value=json.loads(raw);text=raw.decode('utf8')
    def block(item):return '\n'.join('    '+v for v in json.dumps(item,indent=2,ensure_ascii=False).splitlines())
    for group,key in [('files','new_file_entry'),('native_units','new_unit_entry')]:
        old=block(value[group][-1]);need(text.count(old)==1,'Unique exact insertion point')
        text=text.replace(old,old+',\n'+block(k[key]));value[group].append(k[key])
    data=text.encode('utf8')
    need(hashlib.sha256(data).hexdigest()==EXPECTED and json.loads(data)==value,'Exact 95-file bytes and content')
    return data
if __name__=='__main__':
    raw=raw_parent()
    print(json.dumps(dict(passed=True,parent_sha256=EXPECTED,current_manifest_is_parent=(ROOT/'src/source-manifest.json').read_bytes()==raw,Git_history_written=False)))
