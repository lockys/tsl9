"""Read-only delivery identity check, only writes new local review JSON."""
from pathlib import Path
import json, hashlib
ROOT=Path('C:/Users/locky/Documents/projects/re-tsl9')
DELIVERY=ROOT/'candidate-bin/ch32v208-2026-10-20'
OUT=Path(__file__).parent/'delivery-review.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(ok,msg):
    if not ok:raise AssertionError(msg)
m=json.loads((DELIVERY/'manifest.json').read_text(encoding='utf-8-sig'))
checked=[]
for name,r in m['outputs'].items():
    p=Path(r['path']);source=Path(r['source'])
    check(p.parent==DELIVERY and p.name==name,'delivery target')
    check(p.stat().st_size==r['bytes'] and sha(p)==sha(source)==r['sha256'],'copy identity '+name)
    checked.append(dict(name=name,bytes=r['bytes'],sha256=sha(p),source=str(source)))
for record in m['actual_builds']:
    check(sha(record['producer'])==record['producer_sha256'],'producer receipt hash')
    check(sha(record['audit'])==record['audit_sha256'],'audit receipt hash identity only')
    check(sha(record['binary']['path'])==record['binary']['sha256'],'build BIN hash')
    check(record['guarded_core_source_count']==98,'98 guarded sources each language')
for name,digest in m['unchanged_original_manifests'].items():check(sha(ROOT/name)==digest,'original manifest guard')
for name in ('high_level_source_fully_recovered','new_features_added','includes_BOOT_ROOT_ROM','target_ready','ota_verified','goal_complete','target_executed','hardware','network'):check(m[name] is False,'claim boundary '+name)
check(m['guarded_core_source_counts']==dict(c=98,cpp=98),'source count distinction')
check(m['unknown_table_tail_bytes']==272 and m['source_external_bytes']==0,'missing bytes stay absent')
check(not OUT.exists(),'new receipt only')
result=dict(schema='independent-delivery-copy-review-v1',passed=True,manifest_sha256=sha(DELIVERY/'manifest.json'),checked_copies=checked,original_manifest_hashes_preserved=True,dual_language_receipt_hashes_verified=True,guarded_core_source_counts=m['guarded_core_source_counts'],claims_remain_experimental=True,network=False,target_executed=False,hardware=False,emulation=False,build_performed_by_reviewer=False)
OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(passed=True,checked_copies=len(checked),review=str(OUT))))
