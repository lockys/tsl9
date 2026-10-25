"""Reconstruct the exact141-file precursor without source or Git mutation."""
from pathlib import Path
import hashlib,json,runpy
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS=ROOT/'experiments/tsl9-input-state-decoders/parent-manifest-v1.py'
EXTENSION=ROOT/'experiments/tsl9-input-state-decoders/source-extension-v1.json'
P_SHA='c64e8338149794d1714a97f82e566cc2f9f558e96d7fa1893033e3b3390651e4'
K_SHA='1dd5d13d80bd5c0b832e1357b8eed21cc97d08966183d3a3d77feff1ffa04663'
EXPECTED='5921681d6259c7eca531526c3da4cb59100938d32666a58557bb9163f655e72f'
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
 need(hashlib.sha256(result).hexdigest()==EXPECTED==k['new_manifest_sha256']and json.loads(result)==value,'Exact141-file original bytes')
 return result
if __name__=='__main__':print(json.dumps(dict(passed=bool(raw_parent()),parent_sha256=EXPECTED,files_written=False)))
