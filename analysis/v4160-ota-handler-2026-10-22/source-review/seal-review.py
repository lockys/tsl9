"""Create-only original source/consumer-inspection seal, excluding builds."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not (HERE/'seal.json').exists()
    assert (HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes()
    result=json.loads((HERE/'selected-results.json').read_bytes());assert set(result)=={'default','c','cpp'}
    for r in result.values():
        assert r['passed'] and (r['raw_instructions'],r['source_bytes'],r['raw_semantic_controls'],r['owned_RELA'])==(169,530,8,51)
        assert r['inspected_consumer_source_identities_checked']==4 and not r['actual_native_or_HOST_replayed'] and not r['whole_original_ABI_admitted']
    assert result['default']['actual_original_objects_replayed']==0
    assert all(result[m]['actual_original_objects_replayed']==1 for m in ('c','cpp'))
    for p in HERE.glob('*.md'):assert p.read_bytes().endswith(b'\n') and not p.read_bytes().endswith(b'\n\n')
    members={p.name:sha(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='seal.json'}
    with (HERE/'seal.json').open('xb') as f:f.write((json.dumps(dict(schema='ID2966-OTA-handler-original-source-seal-v1',members=members,source_metadata_only=True,generated_build_artifacts_published=False,target_execution=False),indent=2)+'\n').encode('utf-8'))
    print(json.dumps(dict(passed=True,members=len(members),seal_sha256=sha(HERE/'seal.json'))))
if __name__=='__main__':main()
