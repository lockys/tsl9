#!/usr/bin/env python3
"""Read-only exports/checks for this offline milestone; raw receipts stay local."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
PUBLIC=ROOT/'analysis/feature-callback-2026-10-23'
BASE=ROOT/'scripts/check-record-publication.py'
BASE_SHA='1e725cd4f3eaf211613f340281943132280a4282363c24245eb8d59efb163a5d'
SOURCES={
  "native-c": "experiments/tsl9-feature-callback/build/graph-v2/c/verification.json",
  "native-cpp": "experiments/tsl9-feature-callback/build/graph-v2/cpp/verification.json",
  "integration-build": "experiments/tsl9-feature-callback/build/graph-v2/measurement.json",
  "standalone-trial": "experiments/tsl9-feature-callback/build/trial-v4/measurement.json",
  "historical-failed-v1": "experiments/tsl9-feature-callback/build/trial-v1/measurement.json",
  "historical-failed-v2": "experiments/tsl9-feature-callback/build/trial-v2/measurement.json",
  "curated-source": "build/curated-source/feature-callback-20261023-v2/verification.json"
}
def need(ok,message):
    if not ok:raise ValueError(message)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
need(sha(BASE)==BASE_SHA,'Unchanged shared publication derivation')
B=runpy.run_path(str(BASE),run_name='receive_transmit_publication_library')
B['derive'].__globals__['SOURCES']=SOURCES
def derive(key):
    data,item=B['derive'](key)
    item['public_path']='analysis/feature-callback-2026-10-23/evidence/'+key+'.json'
    return data,item
def metadata():
    return dict(schema='TSL9-feature-callback-publication-provenance-v1',
        exporter='scripts/check-feature-callback-publication.py',exporter_sha256=sha(Path(__file__)),
        shared_exporter='scripts/check-record-publication.py',shared_exporter_sha256=BASE_SHA,
        original_receipts_unchanged=True,originals_preserved_local=True,Git_history_rewritten=False,
        files=[derive(k)[1] for k in SOURCES])
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--emit',choices=SOURCES)
    p.add_argument('--offset',type=int,default=0);p.add_argument('--limit',type=int,default=16000);p.add_argument('--metadata',action='store_true');a=p.parse_args()
    if a.metadata:print(json.dumps(metadata(),ensure_ascii=True));return
    if a.emit:
        need(a.offset>=0 and 0<a.limit<=20000,'Bounded export slice')
        data,item=derive(a.emit);print(json.dumps(data.decode('utf8')[a.offset:a.offset+a.limit],ensure_ascii=True));return
    facts=metadata();need(json.loads((PUBLIC/'publication-provenance.json').read_bytes())==facts,'Current complete original/public provenance')
    for key in SOURCES:
        data,item=derive(key);need((ROOT/item['public_path']).read_bytes()==data,'Exact intended public bytes '+key)
    print(json.dumps(dict(passed=True,files=len(SOURCES),
        portable_originals=sum(x['receipt_is_original'] for x in facts['files']),
        path_only_derivatives=sum(not x['receipt_is_original'] for x in facts['files']),
        absolute_personal_path_findings=0,originals_preserved_local=True,raw_replay_claimed_for_derivatives=False)))
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError) as e:print('FAIL: '+str(e),file=sys.stderr);sys.exit(1)
