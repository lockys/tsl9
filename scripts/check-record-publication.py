#!/usr/bin/env python3
"""Read-only publication derivation/check; originals and all build files stay local."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT/'analysis/record-dispatch-2026-10-23'
SOURCES = {
    'record-c': 'experiments/tsl9-record-dispatch/build/verified-v1/c/verification.json',
    'record-cpp': 'experiments/tsl9-record-dispatch/build/verified-v1/cpp/verification.json',
    'predicate-c': 'experiments/tsl9-record-predicate/build/verified-v3/c/verification.json',
    'predicate-cpp': 'experiments/tsl9-record-predicate/build/verified-v3/cpp/verification.json',
    'component-c': 'experiments/tsl9-record-dispatch-component/build/component-v1/c/verification.json',
    'component-cpp': 'experiments/tsl9-record-dispatch-component/build/component-v1/cpp/verification.json',
    'curated-source': 'build/curated-source/record-dispatch-20261023-v1/verification.json',
}
PRIVATE = re.compile(r'(?i)(?<![a-z0-9_])[a-z]:[/\\\\]|/(?:users|home)/')
def need(ok, message):
    if not ok:
        raise ValueError(message)
def digest(raw):
    return hashlib.sha256(raw).hexdigest()
def encoded(value):
    return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=True)+'\n').encode()
def replacements():
    llvm = Path.home()/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin'
    pairs = []
    for name,path in [('CLANG_RESOURCE',llvm.parent/'lib/clang/18'),('LLVM_BIN',llvm),('TSL9_ROOT',ROOT)]:
        forms = [(str(path),'WINDOWS'),(path.as_posix(),'POSIX')]
        for prefix,style in forms:
            if prefix not in [p for p,t in pairs]:
                pairs.append((prefix,'$'+'{PUBLIC_'+name+'_'+style+'}'))
    return pairs
def tree(value, pairs):
    if isinstance(value,str):
        for before,after in pairs:
            value = value.replace(before,after)
        return value
    if isinstance(value,list):
        return [tree(x,pairs) for x in value]
    if isinstance(value,dict):
        items = [(tree(k,pairs),tree(v,pairs)) for k,v in value.items()]
        need(len({k for k,v in items}) == len(items),'No substituted key collisions')
        return dict(items)
    return value
def derive(key):
    original = ROOT/SOURCES[key]
    raw = original.read_bytes()
    need(raw.endswith(b'\n') and not raw.endswith(b'\n\n'),'Single original EOF')
    if not PRIVATE.search(raw.decode('utf8')):
        data = raw
        kind = 'portable-original-exact-bytes'
        inverse = True
    else:
        value = json.loads(raw)
        pairs = replacements()
        need(all(t not in raw.decode('utf8') for p,t in pairs),'Fresh disjoint placeholders')
        clean = tree(value,pairs)
        inverse = tree(clean,[(t,p) for p,t in reversed(pairs)]) == value
        need(inverse,'Inverse complete JSON equality')
        data = encoded(dict(schema='TSL9-path-only-public-receipt-derivative-v1',
            original_local_receipt=SOURCES[key],original_sha256=digest(raw),original_bytes=len(raw),
            originals_preserved_local=True,receipt_is_original=False,original_replay_claimed=False,
            path_only_redaction=True,inverse_JSON_equality_verified=True,
            substitutions=[dict(placeholder=t,meaning='Local '+t.split('PUBLIC_',1)[1].rstrip('}')+' prefix') for p,t in pairs],
            receipt=clean))
        kind = 'path-only-JSON-derivative'
    need(not PRIVATE.search(data.decode('utf8')),'No public absolute paths')
    return data,dict(key=key,public_path='analysis/record-dispatch-2026-10-23/evidence/'+key+'.json',
        original_local_path=SOURCES[key],original_sha256=digest(raw),original_bytes=len(raw),
        public_sha256=digest(data),public_bytes=len(data),kind=kind,
        receipt_is_original=kind=='portable-original-exact-bytes',
        original_replay_claimed=False,inverse_JSON_equality_verified=inverse)
def metadata():
    return dict(schema='TSL9-record-publication-provenance-v1',
        exporter='scripts/check-record-publication.py',exporter_sha256=digest(Path(__file__).read_bytes()),
        original_receipts_unchanged=True,originals_preserved_local=True,
        Git_history_rewritten=False,files=[derive(k)[1] for k in SOURCES])
def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--emit',choices=SOURCES)
    p.add_argument('--offset',type=int,default=0)
    p.add_argument('--limit',type=int,default=16000)
    p.add_argument('--metadata',action='store_true')
    a = p.parse_args()
    if a.metadata:
        print(json.dumps(metadata(),ensure_ascii=True))
        return
    if a.emit:
        need(a.offset>=0 and 0<a.limit<=20000,'Bounded output slice')
        data,_ = derive(a.emit)
        print(json.dumps(data.decode('utf8')[a.offset:a.offset+a.limit],ensure_ascii=True))
        return
    saved = json.loads((PUBLIC/'publication-provenance.json').read_bytes())
    need(saved == metadata(),'Current original/public provenance identities')
    for key in SOURCES:
        data,item = derive(key)
        need((ROOT/item['public_path']).read_bytes() == data,'Exact intended public bytes '+key)
    print(json.dumps(dict(passed=True,files=7,portable_originals=4,path_only_derivatives=3,
        originals_preserved_local=True,raw_replay_claimed_for_derivatives=False,absolute_path_findings=0)))
if __name__ == '__main__':
    try:
        main()
    except (ValueError,OSError,KeyError) as error:
        print('FAIL: '+str(error),file=sys.stderr)
        sys.exit(1)
