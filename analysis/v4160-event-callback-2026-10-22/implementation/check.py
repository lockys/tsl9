#!/usr/bin/env python3
"""Source/metadata by default; explicit real HOST/native archives on request."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;MODEL='experiments/tsl9-v4160-event-callback'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def read(p):return json.loads(p.read_bytes())
def case(root,slug):return next(p for p in(root/'analysis'/slug,root/'apk-analysis'/('tsl9-'+slug)) if p.is_dir())
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--host-receipt',type=Path,action='append',default=[]);p.add_argument('--native-receipt',type=Path,action='append',default=[]);p.add_argument('--require-local-builds',action='store_true');a=p.parse_args();root=a.project_root.resolve();seal=read(HERE/'seal.json');model=root/MODEL
    for n,pin in seal['members'].items():need(sha(HERE/n)==pin,'exact implementation source/metadata member')
    for n,pin in seal['model_members'].items():need(sha(model/n)==pin,'exact model source/test/wrapper member')
    for item in seal['independent_seals']:
        folder=case(root,item['case'])/item['scope'];s=folder/'seal.json';need(sha(s)==item['sha256'],'closed independent evidence seal');r=read(s);members=r.get('members',r.get('files'));members=members.items() if isinstance(members,dict) else ((x['path'],x['sha256']) for x in members)
        for n,pin in members:need(sha(folder/n)==pin,'closed independent source/metadata bytes')
    index=read(HERE/'results.json')
    for r in index['results']:need(sha(HERE/r['metadata'])==r['sha256'] and read(HERE/r['metadata'])['passed'],'selected receipt metadata only')
    old=read(HERE/'receipts/inline-comparison.json')['source_pins'];plain=(model/'src/io.h').read_text().replace('static __attribute__((always_inline)) inline void cb_native_call(','static inline void cb_native_call(');need(hashlib.sha256(plain.encode()).hexdigest()==old['io.h'],'historical comparison baseline is exactly current qualifier removal')
    need((HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes() and(model/'README.md').read_bytes()==(model/'readme.zh-TW.md').read_bytes(),'full Traditional Chinese defaults')
    host=list(a.host_receipt);native=list(a.native_receipt)
    if a.require_local_builds:
        for r in index['results']:(host if r['kind']=='host' else native).append(Path(r['receipt']))
    actual=[]
    if host:
        m=runpy.run_path(str(model/'verify_host.py'))
        for receipt in host:actual.append(m['replay'](root,receipt))
    if native:
        m=runpy.run_path(str(HERE/'verify_native.py'))
        for receipt in native:actual.append(m['replay'](root,receipt))
    print(json.dumps(dict(passed=True,implementation_members=len(seal['members']),model_members=len(seal['model_members']),actual_build_archives_read=bool(actual),actual_replays=actual,native_fit=False,original_ABI_admitted=False,full_image_changed=False,target_execution=False,hardware_OTA_proved=False)))
if __name__=='__main__':main()
