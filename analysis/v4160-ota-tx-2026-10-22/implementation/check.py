#!/usr/bin/env python3
"""Default checks sealed text/metadata only; actual archive replay is explicit."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
MODEL='experiments/tsl9-v4160-ota-tx'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
 if not v:raise ValueError(m)
def read(p):return json.loads(p.read_bytes())
def check(root,here):
 seal=read(here/'seal.json')
 for group,base in [('members',here),('model_members',root/MODEL)]:
  for n,pin in seal[group].items():p=(base/n).resolve();need(p.is_relative_to(base.resolve()) and sha(p)==pin,'sealed '+group+' '+n)
 for row in seal['references']:need(sha(here.parent/row['path'])==row['sha256'],'immutable independent reference '+row['path'])
 selected=read(here/'results.json');need(len(selected['results'])==4,'selected four source-matched receipts')
 for row in selected['results']:
  p=here/row['metadata'];r=read(p);need(sha(p)==row['sha256'] and r['mode']==row['mode'] and r['passed'],'byte-identical selected receipt metadata')
  if row['kind']=='native':need(r['checks']['actual_bytes']==280 and not r['checks']['whole_original_ABI_admitted'] and not r['checks']['full_image_integration'],'partial native status remains explicit')
 return dict(passed=True,seal_sha256=sha(here/'seal.json'),members=len(seal['members']),model_members=len(seal['model_members']),actual_build_archives_read=False,actual_HOST_executables_run=False,actual_RV32_executed=False,original_ABI_admitted=False)
def main():
 p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=Path(__file__).resolve().parents[3]);p.add_argument('--require-local-builds',action='store_true');p.add_argument('--receipt',type=Path,action='append');p.add_argument('--firmware',type=Path);a=p.parse_args();root=a.project_root.resolve();here=Path(__file__).resolve().parent;r=check(root,here);need(not(a.receipt and a.require_local_builds),'choose explicit receipt or historical local archives');receipts=a.receipt or ([Path(x['receipt']) for x in read(here/'results.json')['results']] if a.require_local_builds else []);need(a.firmware is None or receipts,'firmware only applies to explicit native archive replay');replayed=[]
 for receipt in receipts:
  receipt=receipt.resolve();record=read(receipt)
  if record['schema']=='TSL9-OTA-TX-synthetic-host-v1':m=runpy.run_path(str(root/MODEL/'verify_host.py'));replayed.append(m['replay'](root,receipt))
  elif record['schema']=='TSL9-OTA-TX-partial-native-v1':m=runpy.run_path(str(here/'verify_native.py'));replayed.append(m['replay'](root,receipt,a.firmware))
  else:raise ValueError('unsupported actual receipt schema')
 if replayed:r['actual_build_archives_read']=True;r['replays']=replayed
 print(json.dumps(r))
if __name__=='__main__':main()
