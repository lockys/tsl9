"""Reconstruct the exact134-file precursor without source or Git mutation."""
from pathlib import Path
import hashlib,json,runpy
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS=ROOT/'experiments/tsl9-feature-state-records/parent-manifest-v1.py'
EXTENSION=ROOT/'experiments/tsl9-feature-state-records/source-extension-v1.json'
P_SHA='55d5a156d172168e9d33e97aa7faf75de3535b4327a08c6295436780588ad1d4'
K_SHA='bf180b1574265dd2730a78918c5c3ee6d98eb8039873066cd5e4f2889593a416'
EXPECTED='5bfe9e580fdeb8e3e4296cb96ec45e2a34ffbc6736af7745d8e689bb9bb52ab2'
def need(x,label):
 if not x:raise ValueError(label)
def raw_parent():
 need(hashlib.sha256(PREVIOUS.read_bytes()).hexdigest()==P_SHA,'Pinned previous manifest reconstruction')
 need(hashlib.sha256(EXTENSION.read_bytes()).hexdigest()==K_SHA,'Pinned previous exact extension')
 k=json.loads(EXTENSION.read_bytes());raw=runpy.run_path(str(PREVIOUS))['raw_parent']()
 need(hashlib.sha256(raw).hexdigest()==k['previous_manifest_sha256'],'Exact retained precursor')
 value=json.loads(raw);text=raw.decode('utf-8')
 def block(v):return '\n'.join('    '+line for line in json.dumps(v,indent=2,ensure_ascii=False).splitlines())
 for group,key in [('files','new_file_entry'),('native_units','new_unit_entry')]:
  old=block(value[group][-1]);need(text.count(old)==1,'One exact insertion site')
  text=text.replace(old,old+',\n'+block(k[key]));value[group].append(k[key])
 result=text.encode('utf-8')
 need(hashlib.sha256(result).hexdigest()==EXPECTED==k['new_manifest_sha256']and json.loads(result)==value,'Exact134-file original bytes')
 return result
if __name__=='__main__':print(json.dumps(dict(passed=bool(raw_parent()),parent_sha256=EXPECTED,files_written=False)))
