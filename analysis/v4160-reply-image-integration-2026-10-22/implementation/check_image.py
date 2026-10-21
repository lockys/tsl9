#!/usr/bin/env python3
"""Read-only metadata by default; actual generated artifact replay is explicit."""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('twelve_image_readonly_verifier',H/'verify_image.py');V=importlib.util.module_from_spec(s);s.loader.exec_module(V)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(value):
 data=value.get('members',value.get('files'))
 return [dict(path=n,sha256=r if isinstance(r,str) else r['sha256']) for n,r in data.items()] if isinstance(data,dict) else data
def check(root,require_local_builds=False,receipts=(),firmware=None):
 seal=V.read(H/'seal.json');index=V.read(H/'results.json');ctx=V.context(root,firmware)
 for row in seal['members']:
  p=(H/row['path']).resolve();V.need(p.is_relative_to(H) and p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],'sealed implementation member')
 for row in seal['model_members']:
  p=(root/row['path']).resolve();V.need(p.is_relative_to(root) and p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],'sealed model member')
 for row in seal['independent_review_seals']:
  p=H/row['path'];V.need(sha(p)==row['sha256'],'closed independent review seal')
  for item in rows(V.read(p)):V.need(sha(p.parent/item['path'])==item['sha256'],'closed independent member')
 V.need(len(index['results'])==2 and index['manifest_sha256']==V.MANIFEST_SHA,'exact selected C/C++ ledger metadata');available=[];replayed=[]
 for row in index['results']:
  p=H/row['metadata'];V.need(sha(p)==row['sha256'],'selected receipt byte identity');r=V.read(p);V.need(r['passed'] and r['mode']==row['mode'] and r['runner_sha256']==sha(H/'verify_image.py') and r['manifest_sha256']==V.MANIFEST_SHA and r['source_files']==ctx['manifest']['source_files'],'current selected native source/runner/manifest identity')
  V.need((r['checks']['merged']['allocations'],r['checks']['merged']['retained_storage_sections'],r['checks']['merged']['RELA'],r['checks']['actual_commands']['compile_TUs'],r['checks']['actual_commands']['commands'])==(691,679,8269,43,61),'selected measured image proof inventory');V.need(r['checks']['image']['sha256']==index['image_sha256'] and not r['checks']['image']['differences'],'selected original-identical source image metadata')
  actual=root/row['artifact_dir']/'verification.json';available.append(dict(mode=row['mode'],available=actual.is_file()))
  if require_local_builds:V.need(actual.is_file() and sha(actual)==row['sha256'],'required selected local archive available');replayed.append(V.replay(root,actual,firmware))
 option=index['CLI_options'];V.need(sha(H/option['metadata'])==option['sha256'],'selected readonly CLI metadata');report=V.read(H/option['metadata']);V.need(report['passed'] and report['runner_sha256']==sha(H/'verify_image.py') and report['script_sha256']==sha(H/'test_cli.py') and len(report['records'])==5,'selected CLI regression identities')
 if require_local_builds:
  base=root/option['artifact_dir'];V.need(sha(base/'verification.json')==option['sha256'],'actual selected CLI receipt')
  for c in report['records']:V.need(sha(base/c['log'])==c['log_sha256'],'actual readonly CLI log')
 for receipt in receipts:replayed.append(V.replay(root,receipt.resolve(),firmware))
 return dict(passed=True,seal_sha256=sha(H/'seal.json'),metadata_only=not bool(require_local_builds or receipts),actual_selected_archives=available,actual_archive_replays=replayed,image_sha256=index['image_sha256'],readable_functions=12,readable_function_bytes=650,storage_bytes=76800,differences=0,compiler_plus_two_explicit_ABI_stages=True,ROM_provider=False,flashable=False,OTA_ready=False,target_execution=False)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=H.parents[2]);p.add_argument('--firmware',type=Path);p.add_argument('--require-local-builds',action='store_true');p.add_argument('--receipt',type=Path,action='append',default=[]);a=p.parse_args();print(json.dumps(check(a.project_root.resolve(),a.require_local_builds,a.receipt,a.firmware)))
