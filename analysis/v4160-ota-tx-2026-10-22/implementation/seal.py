#!/usr/bin/env python3
"""Create once, or check, a source/metadata-only implementation seal."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=Path(__file__).resolve().parents[3]);p.add_argument('--create',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args();root=a.project_root.resolve();here=Path(__file__).resolve().parent
 if a.create:
  if (here/'seal.json').exists():raise ValueError('seal already exists')
  names=['verify_native.py','check.py','check.sh','seal.py','close_evidence.py','README.md','readme.zh-TW.md','readme.en.md','results.json',*[p.relative_to(here).as_posix() for p in sorted((here/'receipts').glob('*.json'))]]
  model=root/'experiments/tsl9-v4160-ota-tx';members=['.gitignore','verify_host.py','verify_native.py','verify.sh','verify_native.sh','README.md','readme.zh-TW.md','readme.en.md',*[p.relative_to(model).as_posix() for d in ('src','tests') for p in sorted((model/d).glob('*')) if p.is_file()]]
  refs=[dict(path=n+'/seal.json',sha256=sha(here.parent/n/'seal.json')) for n in ('source-review','source-review-v2','code-review','ABI-review')]
  r=dict(schema='TSL9-OTA-TX-partial-implementation-seal-v1',members={n:sha(here/n) for n in names},model_members={n:sha(model/n) for n in members},references=refs,generated_builds_included=False,original_ABI_admitted=False,full_image_integration=False,RV32_execution=False)
  (here/'seal.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
 print(json.dumps(runpy.run_path(str(here/'check.py'))['check'](root,here)))
if __name__=='__main__':main()
