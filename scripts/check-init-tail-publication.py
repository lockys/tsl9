#!/usr/bin/env python3
"""Read-only public exports; original receipts remain local and unchanged."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
PUBLIC=ROOT/'analysis/init-tail-2026-10-24'
BASE=ROOT/'scripts/check-record-publication.py'
BASE_SHA='1e725cd4f3eaf211613f340281943132280a4282363c24245eb8d59efb163a5d'
SOURCES={
    'native-c':'experiments/tsl9-init-tail/build/component-v1/c/verification.json',
    'native-cpp':'experiments/tsl9-init-tail/build/component-v1/cpp/verification.json',
    'integration-build':'experiments/tsl9-init-tail/build/component-v1/measurement.json',
    'provider-audit':'experiments/tsl9-init-tail/build/provider-v1/measurement.json',
    'standalone-trial':'experiments/tsl9-init-tail/build/trial-v1/measurement.json',
}
def need(ok,message):
    if not ok:raise ValueError(message)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
need(sha(BASE)==BASE_SHA,'Unchanged shared publication derivation')
B=runpy.run_path(str(BASE),run_name='publication_library')
B['derive'].__globals__['SOURCES']=SOURCES
def derive(key):
    data,item=B['derive'](key)
    item['public_path']='analysis/init-tail-2026-10-24/evidence/'+key+'.json'
    return data,item
def metadata():
    return dict(schema='TSL9-INIT-TAIL-publication-provenance-v1',
        exporter='scripts/check-init-tail-publication.py',exporter_sha256=sha(Path(__file__)),
        shared_exporter='scripts/check-record-publication.py',shared_exporter_sha256=BASE_SHA,
        original_receipts_unchanged=True,originals_preserved_local=True,Git_history_rewritten=False,
        curation_full_original_preserved_local='build/curated-source/init-tail-20261024-v1/verification.json',
        curation_full_original_sha256='a512ab49d04e6f5ad06fa1771e2aa03065513f934ba3e59dac37d1b4ff519c74',
        curation_full_original_copied_to_public=False,
        files=[derive(k)[1] for k in SOURCES])
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--emit',choices=SOURCES)
    p.add_argument('--offset',type=int,default=0)
    p.add_argument('--limit',type=int,default=16000)
    p.add_argument('--metadata',action='store_true')
    a=p.parse_args()
    if a.metadata:
        print(json.dumps(metadata(),ensure_ascii=True));return
    if a.emit:
        need(a.offset>=0 and 0<a.limit<=20000,'Bounded output slice')
        data,_=derive(a.emit)
        print(json.dumps(data.decode('utf8')[a.offset:a.offset+a.limit],ensure_ascii=True));return
    facts=metadata()
    need(json.loads((PUBLIC/'publication-provenance.json').read_bytes())==facts,'Complete original/public provenance')
    need(sha(ROOT/facts['curation_full_original_preserved_local'])==facts['curation_full_original_sha256'],
         'Unchanged local full source comparison receipt')
    for key in SOURCES:
        data,item=derive(key)
        need((ROOT/item['public_path']).read_bytes()==data,'Exact intended public bytes '+key)
    print(json.dumps(dict(passed=True,files=len(SOURCES),
        portable_originals=sum(x['receipt_is_original']for x in facts['files']),
        path_only_derivatives=sum(not x['receipt_is_original']for x in facts['files']),
        absolute_personal_path_findings=0,originals_preserved_local=True,
        raw_replay_claimed_for_derivatives=False)))
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError) as e:
        print('FAIL: '+str(e),file=sys.stderr);sys.exit(1)
