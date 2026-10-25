"""Reconstruct the exact153-file precursor without source or Git mutation."""
from pathlib import Path
import hashlib,json,runpy
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS=ROOT/'experiments/tsl9-callback-prefix-data/parent-manifest-v2.py'
EXTENSION=ROOT/'experiments/tsl9-callback-prefix-data/source-extension-v2.json'
P_SHA='a59f2d3151f9ee6fd4d03fabae8a789ef1e59d870e75b53398c59399d2d35d9a'
K_SHA='aebf5a4cc2e16418ed2c5b1e412423ad41ea9edeb0e4340a8cd57ce71cc3b32c'
EXPECTED='6af9f8e442044d4a67202b164d887d08de6ecb6d324e9058f1b724302afffab3'
def need(x,label):
 if not x:raise ValueError(label)
def raw_parent():
 need(hashlib.sha256(PREVIOUS.read_bytes()).hexdigest()==P_SHA,'Pinned previous manifest reconstruction')
 need(hashlib.sha256(EXTENSION.read_bytes()).hexdigest()==K_SHA,'Pinned previous exact extension')
 k=json.loads(EXTENSION.read_bytes());raw=runpy.run_path(str(PREVIOUS))['raw_parent']()
 need(hashlib.sha256(raw).hexdigest()==k['previous_manifest_sha256'],'Exact retained precursor')
 value=json.loads(raw);text=raw.decode('utf-8')
 def block(v):return '\n'.join('    '+line for line in json.dumps(v,indent=2,ensure_ascii=False).splitlines())
 for group,key in [('files','new_file_entry'),(k.get('unit_collection','native_units'),'new_unit_entry')]:
  old=block(value[group][-1]);need(text.count(old)==1,'One exact insertion site')
  text=text.replace(old,old+',\n'+block(k[key]));value[group].append(k[key])
 result=text.encode('utf-8')
 need(hashlib.sha256(result).hexdigest()==EXPECTED==k['new_manifest_sha256']and json.loads(result)==value,'Exact153-file original bytes')
 return result
if __name__=='__main__':print(json.dumps(dict(passed=bool(raw_parent()),parent_sha256=EXPECTED,files_written=False)))
