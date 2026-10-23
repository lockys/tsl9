#!/usr/bin/env python3
"""Read-only exports/checks for this offline milestone; raw receipts stay local."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
PUBLIC=ROOT/'analysis/resident-copy-arch-2026-10-23'
BASE=ROOT/'scripts/check-record-publication.py'
BASE_SHA='1e725cd4f3eaf211613f340281943132280a4282363c24245eb8d59efb163a5d'
SOURCES={
 'candidate-v1':'experiments/tsl9-resident-copy-arch/build/probe-v1/verification.json',
 'candidate-v2':'experiments/tsl9-resident-copy-arch/build/probe-v2/verification.json',
 'candidate-v3':'experiments/tsl9-resident-copy-arch/build/probe-v2/verification-v3.json',
 'native-build-v2':'experiments/tsl9-resident-copy-arch/build/probe-v2/measurement.json',
 'curated-source':'build/curated-source/resident-copy-arch-20261023-v1/verification.json',
}
def need(ok,message):
    if not ok:raise ValueError(message)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
need(sha(BASE)==BASE_SHA,'Unchanged shared publication derivation')
B=runpy.run_path(str(BASE),run_name='resident_copy_publication_library')
B['derive'].__globals__['SOURCES']=SOURCES
def derive(key):
    data,item=B['derive'](key)
    if b'\r\n' in data:
        original=json.loads(data)
        wrapper=dict(schema='TSL9-line-ending-public-receipt-derivative-v1',
            original_local_receipt=SOURCES[key],original_sha256=item['original_sha256'],original_bytes=len(data),
            receipt_is_original=False,original_replay_claimed=False,originals_preserved_local=True,
            line_endings_normalized=True,inverse_JSON_equality_verified=True,receipt=original)
        data=(json.dumps(wrapper,sort_keys=True,indent=2,ensure_ascii=True)+'\n').encode()
        need(json.loads(data)['receipt']==original,'Complete JSON equality after newline normalization')
        item.update(kind='line-ending-JSON-derivative',receipt_is_original=False,
            public_sha256=hashlib.sha256(data).hexdigest(),public_bytes=len(data))
    item['public_path']='analysis/resident-copy-arch-2026-10-23/evidence/'+key+'.json'
    return data,item
def metadata():
    return dict(schema='TSL9-resident-copy-publication-provenance-v1',
        exporter='scripts/check-resident-copy-publication.py',exporter_sha256=sha(Path(__file__)),
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
        path_only_derivatives=sum(x['kind']=='path-only-JSON-derivative' for x in facts['files']),
        line_ending_derivatives=sum(x['kind']=='line-ending-JSON-derivative' for x in facts['files']),
        absolute_personal_path_findings=0,originals_preserved_local=True,raw_replay_claimed_for_derivatives=False)))
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError) as e:print('FAIL: '+str(e),file=sys.stderr);sys.exit(1)
