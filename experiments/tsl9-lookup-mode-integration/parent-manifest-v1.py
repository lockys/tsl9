"""Reconstruct the exact159-file parent bytes without changing the current manifest."""
import hashlib,json,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def need(ok,label):
    if not ok:raise ValueError(label)
def raw_parent():
    folder=ROOT/'experiments/tsl9-safe-gap-functions';p=folder/'parent-manifest-v1.py';k=folder/'source-extension-v1.json'
    pins=json.loads((Path(__file__).resolve().parent/'source-extension-v1.json').read_bytes())['parent_reconstruction_pins']
    for x in [p,k]:need(hashlib.sha256(x.read_bytes()).hexdigest()==pins[x.relative_to(ROOT).as_posix()],'Frozen159-file parent reconstruction input')
    ext=json.loads(k.read_bytes());raw=runpy.run_path(str(p),run_name='exact158_parent')['raw_parent']();need(hashlib.sha256(raw).hexdigest()==ext['previous_manifest_sha256'],'Exact158-file ancestor')
    value=json.loads(raw);text=raw.decode('utf-8')
    def block(x):return '\n'.join('    '+line for line in json.dumps(x,indent=2,ensure_ascii=False).splitlines())
    for group,key in [('files','new_file_entries'),('native_units','new_CODE_unit_entries'),('native_data_units','new_DATA_unit_entries')]:
        if not ext[key]:continue
        old=block(value[group][-1]);need(text.count(old)==1,'Unique exact parent insertion site');text=text.replace(old,old+',\n'+',\n'.join(block(x)for x in ext[key]));value[group]+=ext[key]
    out=text.encode();need(hashlib.sha256(out).hexdigest()==ext['new_manifest_sha256']=='9a236345dc8618eac74f3d0ed884294d71e1b37b6dead078dafe1bc447d30689'and json.loads(out)==value,'Exact159-file parent bytes and content');return out
