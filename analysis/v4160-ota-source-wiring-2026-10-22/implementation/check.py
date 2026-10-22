#!/usr/bin/env python3
"""Default source/metadata-only check; explicit receipt replays actual artifacts."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
MODEL='experiments/tsl9-v4160-ota-source-wiring'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--receipt',action='append',type=Path,default=[]);a=p.parse_args();root=a.project_root.resolve();seal=json.loads((HERE/'seal.json').read_bytes())
    for base,key in((HERE,'members'),(root/MODEL,'model_members')):
        for name,pin in seal[key].items():
            path=(base/name).resolve();need(path.is_relative_to(base.resolve()) and H(path)==pin,'Exact source/member '+name)
    for row in seal['dependencies']:
        path=next((root/name for name in row['paths'] if (root/name).is_file()),None);need(path is not None and H(path)==row['sha256'],'Exact portable dependency '+row['paths'][0])
    for row in seal['independent_seals']:
        base=HERE.parent/row['scope'];path=base/'seal.json';need(H(path)==row['sha256'],'Exact independent seal '+row['scope']);r=json.loads(path.read_bytes());members=r.get('members') or {x['path']:x['sha256'] for x in r['files']}
        for name,pin in members.items():
            member=(base/name).resolve();need(member.is_relative_to(base.resolve()) and H(member)==pin,'Independent source/member '+name)
    index=json.loads((HERE/'results.json').read_bytes());need(len(index['results'])==2,'Two selected formal language metadata receipts')
    for row in index['results']:
        path=HERE/row['metadata'];need(H(path)==row['sha256'],'Byte-identical selected receipt metadata');r=json.loads(path.read_bytes());q=r['checks'];need(r['passed'] and r['mode']==row['mode'] and q['witness']['image_bytes']==77824 and q['witness']['actual_reroute'] and not q['ROM_provider'],'Source-wired numeric witness metadata only')
    module=runpy.run_path(str(HERE/'verify_image.py')) if a.receipt else None
    checks=[module['replay'](root,path) for path in a.receipt]
    print(json.dumps(dict(passed=True,metadata_only=not bool(a.receipt),actual_build_artifacts_read=bool(a.receipt),replays=checks,source_entry_wired=True,ROM_provider=False,installed_ROM_proved=False,Flash_NV_free_proved=False,original_ABI_admitted=False,hardware_OTA_proved=False,target_execution=False)))
if __name__=='__main__':main()
