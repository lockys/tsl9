#!/usr/bin/env python3
"""Read-only metadata closure; actual archive replay is explicit and separate."""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
MODEL='experiments/tsl9-v4160-ota-page-reply'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(x,m):
 if not x:raise ValueError(m)
def read(p):return json.loads(p.read_bytes())
def locate(root,rel):
 p=root/rel
 if p.is_file():return p
 if rel.startswith('apk-analysis/tsl9-'):p=root/rel.replace('apk-analysis/tsl9-','analysis/',1)
 need(p.is_file(),'current sealed input '+rel);return p
def load(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def check(root,archives=False,host_receipts=(),native_receipts=()):
 here=Path(__file__).resolve().parent;seal=read(here/'seal.json');count=0
 for n,pin in seal['members'].items():need(sha(here/n)==pin,'implementation sealed member '+n);count+=1
 for n,pin in seal['model_members'].items():need(sha(root/MODEL/n)==pin,'model sealed member '+n);count+=1
 for n,pin in seal['external_members'].items():need(sha(locate(root,n))==pin,'independent proof dependency '+n);count+=1
 need((root/MODEL/'README.md').read_bytes()==(root/MODEL/'readme.zh-TW.md').read_bytes() and (here/'README.md').read_bytes()==(here/'readme.zh-TW.md').read_bytes(),'full Traditional Chinese defaults')
 index=read(here/'results.json');available=[];replayed=[];native=load(here/'verify_native.py','reply_checker_native');host=load(root/MODEL/'verify_host.py','reply_checker_host')
 for row in index['results']:
  metadata=here/row['metadata'];need(sha(metadata)==row['sha256'],'byte-identical selected receipt metadata');r=read(metadata);need(r['passed'] and r['mode']==row['mode'],'selected actual result')
  if row['kind']=='native':
   for n,pin in r['input_sha256'].items():need(sha(locate(root,n))==pin,'native selected source/checker identity '+n)
   need(r['checks']['full_original_byte_identity_after_explicit_order'] and r['checks']['provider_witness_only'],'bounded native identity/witness claims')
  else:need(r['source_sha256']==host.source_pins(root/MODEL) and r['runner_sha256']==sha(root/MODEL/'verify_host.py') and r['tests']==host.EXPECTED,'selected host current source and frozen counters')
  actual=root/row['archive_relative'];available.append(dict(kind=row['kind'],mode=row['mode'],available=actual.is_file()))
  if archives:need(actual.is_file() and sha(actual)==row['sha256'],'selected actual archive available in this root');replayed.append((native if row['kind']=='native' else host).replay(root,actual))
 for p in host_receipts:replayed.append(host.replay(root,p.resolve()))
 for p in native_receipts:replayed.append(native.replay(root,p.resolve()))
 return dict(passed=True,seal_sha256=sha(here/'seal.json'),members_checked=count,selected_metadata=4,actual_selected_archives=available,actual_archive_replays=replayed,metadata_only=not bool(archives or host_receipts or native_receipts),RV32_execution=False,hardware=False,OTA_ready=False)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path);p.add_argument('--archives',action='store_true');p.add_argument('--host-receipt',action='append',type=Path,default=[]);p.add_argument('--native-receipt',action='append',type=Path,default=[]);a=p.parse_args();print(json.dumps(check(a.project_root.resolve(),a.archives,a.host_receipt,a.native_receipt)))
