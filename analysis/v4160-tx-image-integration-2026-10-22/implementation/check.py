#!/usr/bin/env python3
"""Default source/metadata closure; actual artifact replay is opt-in."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;MODEL='experiments/tsl9-v4160-tx-image-integration'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def read(p):return json.loads(p.read_bytes())
def case(root,slug):return next(p for p in(root/'analysis'/slug,root/'apk-analysis'/('tsl9-'+slug)) if p.is_dir())
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--firmware',type=Path);p.add_argument('--receipt',type=Path,action='append',default=[]);p.add_argument('--require-local-builds',action='store_true');a=p.parse_args();root=a.project_root.resolve();seal=read(HERE/'seal.json')
    for n,pin in seal['members'].items():need(sha(HERE/n)==pin,'exact implementation member '+n)
    for n,pin in seal['model_members'].items():need(sha(root/MODEL/n)==pin,'exact model member '+n)
    for r in seal['independent_seals']:
        folder=case(root,r['case'])/r['scope'];s=folder/'seal.json';need(sha(s)==r['sha256'],'closed independent review identity');closed=read(s);members=closed.get('members',closed.get('files'));need(members is not None,'explicit independent file inventory');members=members.items() if isinstance(members,dict) else ((x['path'],x['sha256']) for x in members)
        for n,pin in members:need(sha(folder/n)==pin,'closed independent source/metadata member')
    ledger=read(root/MODEL/'source-manifest.json')
    for n,pin in ledger['source_files'].items():need(sha(root/n)==pin,'source/header ledger pin')
    index=read(HERE/'results.json')
    for r in index['results']:need(sha(HERE/r['metadata'])==r['sha256'] and read(HERE/r['metadata'])['passed'],'selected receipt metadata identity only')
    need((root/MODEL/'README.md').read_bytes()==(root/MODEL/'readme.zh-TW.md').read_bytes() and(HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes(),'full Traditional Chinese default documents')
    receipts=list(a.receipt)
    if a.require_local_builds:receipts += [Path(r['receipt']) for r in index['results']]
    actual=[]
    if receipts:
        m=runpy.run_path(str(HERE/'verify_image.py'))
        for receipt in receipts:actual.append(m['replay'](root,receipt,a.firmware))
    print(json.dumps(dict(passed=True,implementation_members=len(seal['members']),model_members=len(seal['model_members']),actual_build_archives_read=bool(actual),actual_replays=actual,target_execution=False,whole_original_ABI_admitted=False,hardware_OTA_proved=False)))
if __name__=='__main__':main()
