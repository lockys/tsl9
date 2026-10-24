"""Reconstruct the exact129-file precursor without source or Git mutation."""
from pathlib import Path
import hashlib,json,runpy
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS=ROOT/'experiments/tsl9-resident-startup/parent-manifest-v1.py'
EXTENSION=ROOT/'experiments/tsl9-resident-startup/source-extension-v1.json'
P_SHA='a64b51e67f081a25f09f53cf1cd11f61324a94ab1090573e7c818bf5e7c49b1f'
K_SHA='fbaec6902e796d045f26cc2ba2bf37aa9143b8473b74945dba7f466545a4ca11'
EXPECTED='cfa7353218c79616bf070fcdd77a61beaf7fec894d80e27667b217fad5bc2e83'
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
 need(hashlib.sha256(result).hexdigest()==EXPECTED==k['new_manifest_sha256']and json.loads(result)==value,'Exact129-file original bytes')
 return result
if __name__=='__main__':print(json.dumps(dict(passed=bool(raw_parent()),parent_sha256=EXPECTED,files_written=False)))
