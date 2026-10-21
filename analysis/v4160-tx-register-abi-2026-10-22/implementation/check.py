#!/usr/bin/env python3
"""Sealed source/metadata check; actual compiled archive replay is explicit."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
MODEL='experiments/tsl9-v4160-tx-register-abi'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def need(v,m):
 if not v:raise ValueError(m)
def check(root,here):
 seal=read(here/'seal.json')
 for key,base in [('members',here),('model_members',root/MODEL)]:
  for n,pin in seal[key].items():p=(base/n).resolve();need(p.is_relative_to(base.resolve()) and sha(p)==pin,'sealed '+key+' '+n)
 for r in seal['references']:need(sha(here.parent/r['path'])==r['sha256'],'independent seal '+r['path'])
 selected=read(here/'results.json');need(len(selected['results'])==2 and {r['mode'] for r in selected['results']}=={'c','cpp'},'two actual selected metadata receipts')
 for row in selected['results']:
  p=here/row['metadata'];r=read(p);need(sha(p)==row['sha256'] and r['schema']=='TSL9-TX-register-ABI-component-v1' and r['mode']==row['mode'] and r['passed'],'byte-identical selected component metadata');need(r['checks']['geometry']==dict(bytes=280,instructions=96) and r['checks']['guard_before_frame'] and r['checks']['source_fresh_restore_frontiers'] and not r['checks']['whole_original_ABI_admitted'] and not r['checks']['BIN_exported'],'scope of actual positive subsets and unadmitted whole ABI')
 return dict(passed=True,seal_sha256=sha(here/'seal.json'),members=len(seal['members']),model_members=len(seal['model_members']),actual_build_archives_read=False,target_execution=False,whole_original_ABI_admitted=False)
def main():
 p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=Path(__file__).resolve().parents[3]);p.add_argument('--require-local-builds',action='store_true');p.add_argument('--receipt',type=Path,action='append');p.add_argument('--firmware',type=Path);a=p.parse_args();root=a.project_root.resolve();here=Path(__file__).resolve().parent;r=check(root,here);need(not(a.require_local_builds and a.receipt),'choose historical local archives or explicit fresh receipt');receipts=a.receipt or([Path(x['receipt']) for x in read(here/'results.json')['results']] if a.require_local_builds else[]);need(a.firmware is None or receipts,'firmware applies to explicit actual archive replay');m=runpy.run_path(str(here/'verify_native.py'));r['replays']=[m['replay'](root,p.resolve(),a.firmware) for p in receipts]
 if receipts:r['actual_build_archives_read']=True
 print(json.dumps(r))
if __name__=='__main__':main()
