#!/usr/bin/env python3
"""Seal this narrow supplement without changing any superseded member."""
from pathlib import Path
import hashlib
import json
HERE=Path(__file__).resolve().parent
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    need(not (HERE/'seal.json').exists(),'Create-only new supplemental seal');correction=json.loads((HERE/'correction.json').read_bytes());source_seal=HERE.parent/'source-review/seal.json';need(sha(source_seal)==correction['source_seal_sha256'],'Old source seal untouched')
    for item in correction['supersedes']:
        p=HERE/item['path'];need(sha(p)==item['sha256'],'Exact untouched superseded member')
        if 'old_value' in item:need(json.loads(p.read_bytes())['recorded_RELA']['external_incoming_role']==item['old_value'],'Exact narrowly superseded JSON field')
        else:need(p.read_text(encoding='utf8').count(item['old_phrase'])==1,'One exact superseded9DF4 phrase')
    facts=correction['confirmed']
    for name in ('original.json','boundary-c.json','boundary-cpp.json'):
        r=json.loads((HERE/'metadata'/name).read_bytes());need(all(r['incoming'][key]==value for key,value in facts.items()),'Retained actual instruction fields');need(len(r['raw_semantic_controls'])==3 and all(x['rejected'] for x in r['raw_semantic_controls']),'Real raw controls')
        if name!='original.json':need(len(r['actual_ELF_controls'])==3 and all(x['rejected'] for x in r['actual_ELF_controls']),'Actual ELF controls')
    need((HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes(),'FullTW default README');members=sorted(p for p in HERE.rglob('*') if p.is_file() and p.name!='seal.json');need(all(p.suffix in ('.py','.sh','.md','.json') for p in members),'Source/metadata only')
    for p in members:
        raw=p.read_bytes();need(b'\r' not in raw and raw.endswith(b'\n') and not raw.endswith(b'\n\n'),'UTF8LF/singleEOFnewline');raw.decode('utf8')
    value={'schema':'TSL9-reply-entry-call-correction-seal-v1','files':[{'path':p.relative_to(HERE).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in members],'default_mode':'metadata-only','actual_build_artifacts_included':False,'old_seals_modified':False,'target_execution':False,'hardware_OTA_validated':False};(HERE/'seal.json').write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps({'passed':True,'members':len(members),'seal_sha256':sha(HERE/'seal.json')}))
if __name__=='__main__':main()
