"""Reconstruct the exact158-file precursor without changing source or Git state."""
from pathlib import Path
import hashlib,json,runpy
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS=ROOT/'experiments/tsl9-secondary-message-data/parent-manifest-v2.py'
EXTENSION=ROOT/'experiments/tsl9-secondary-message-data/source-extension-v2.json'
P_SHA='8bafa96f581d8461ce60948f2afceabb8ede1b947dc178d0e622b6c90eb8a5e8'
K_SHA='c8b1719872a408946731f5883d921e90486ebf36a03d10695973e7107c173509'
EXPECTED='e6f3c9bd5c584d3b81983a757bf346cbb25434383a6eb98e3e4cbdf037ca9e0d'
def need(ok,label):
    if not ok:raise ValueError(label)
def raw_parent():
    need(hashlib.sha256(PREVIOUS.read_bytes()).hexdigest()==P_SHA,'Pinned previous parent reconstruction')
    need(hashlib.sha256(EXTENSION.read_bytes()).hexdigest()==K_SHA,'Pinned previous exact extension')
    k=json.loads(EXTENSION.read_bytes());raw=runpy.run_path(str(PREVIOUS),run_name='previous_exact_manifest')['raw_parent']()
    need(hashlib.sha256(raw).hexdigest()==k['previous_manifest_sha256'],'Exact156-file precursor')
    value=json.loads(raw);text=raw.decode('utf-8')
    def block(v):return '\n'.join('    '+line for line in json.dumps(v,indent=2,ensure_ascii=False).splitlines())
    for group,key in [('files','new_file_entries'),('native_units','new_CODE_unit_entries'),('native_data_units','new_DATA_unit_entries')]:
        old=block(value[group][-1]);need(text.count(old)==1,'One exact previous insertion site')
        text=text.replace(old,old+',\n'+',\n'.join(block(v) for v in k[key]));value[group]+=k[key]
    result=text.encode('utf-8')
    need(hashlib.sha256(result).hexdigest()==EXPECTED==k['new_manifest_sha256'] and json.loads(result)==value,'Exact158-file original manifest bytes')
    return result
if __name__=='__main__':print(json.dumps(dict(passed=bool(raw_parent()),parent_sha256=EXPECTED,files_written=False)))
