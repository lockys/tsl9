#!/usr/bin/env python3
"""Create a source/metadata-only seal once; never include generated binaries."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=Path(__file__).resolve().parents[3]);p.add_argument('--create',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args();root=a.project_root.resolve();here=Path(__file__).resolve().parent
 if a.create:
  if (here/'seal.json').exists():raise ValueError('create-only immutable seal')
  names=['verify_native.py','probe_adapter.py','probe_ordered.py','check.py','check.sh','seal.py','README.md','readme.zh-TW.md','readme.en.md','results.json',*[p.relative_to(here).as_posix() for p in sorted((here/'receipts').glob('*.json'))]];model=root/'experiments/tsl9-v4160-tx-register-abi';mn=['.gitignore','verify.py','verify.sh','README.md','readme.zh-TW.md','readme.en.md',*[p.relative_to(model).as_posix() for d in('src','adapter','postpass') for p in sorted((model/d).glob('*')) if p.is_file()]];refs=[dict(path=n+'/seal.json',sha256=sha(here.parent/n/'seal.json')) for n in('source-review','ABI-review')];r=dict(schema='TSL9-TX-register-ABI-implementation-seal-v1',members={n:sha(here/n) for n in names},model_members={n:sha(model/n) for n in mn},references=refs,build_archives_included=False,whole_original_ABI_admitted=False,BIN_exported=False,RV32_execution=False);(here/'seal.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
 print(json.dumps(runpy.run_path(str(here/'check.py'))['check'](root,here)))
if __name__=='__main__':main()
