"""Reconstruct the exact150-file precursor without source or Git mutation."""
from pathlib import Path
import hashlib,json,runpy
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS=ROOT/'experiments/tsl9-record-copy-windows/parent-manifest-v3.py'
EXTENSION=ROOT/'experiments/tsl9-record-copy-windows/source-extension-v3.json'
P_SHA='787cd21c15c5ddcb2fb4e76c848ea19b8093b4282301457ae158e677aebeca0e'
K_SHA='dc5149a0739f415ac24f4a02bc91441df41ac4b75a347de11ff403771e9e7b86'
EXPECTED='9490b018aa3c7b37c477ca3d0559c1a94b9be20be50f0eaa01ac53881ed41182'
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
 need(hashlib.sha256(result).hexdigest()==EXPECTED==k['new_manifest_sha256']and json.loads(result)==value,'Exact150-file original bytes')
 return result
if __name__=='__main__':print(json.dumps(dict(passed=bool(raw_parent()),parent_sha256=EXPECTED,files_written=False)))
