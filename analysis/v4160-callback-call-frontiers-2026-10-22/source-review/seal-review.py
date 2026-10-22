"""Create-only seal of this narrow source/metadata supplement."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not (HERE/'seal.json').exists()
    assert (HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes()
    r=json.loads((HERE/'selected-results.json').read_bytes());assert set(r)=={'default','c','cpp'}
    assert not r['default']['actual_candidate_artifact_read']
    for x in r.values():assert x['passed'] and x['new_operand_controls']==3 and not x['whole_call_ABI_proved']
    for mode in ('c','cpp'):assert r[mode]['actual_candidate_artifact_read'] and not r[mode]['datum_live_at_call']
    for p in HERE.glob('*.md'):assert p.read_bytes().endswith(b'\n') and not p.read_bytes().endswith(b'\n\n')
    members={p.name:sha(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='seal.json'}
    with (HERE/'seal.json').open('xb') as f:f.write((json.dumps(dict(schema='ID2966-callback-call-frontier-source-seal-v1',members=members,source_metadata_only=True,generated_build_artifacts_published=False,target_execution=False),indent=2)+'\n').encode())
    print(json.dumps(dict(passed=True,members=len(members),seal_sha256=sha(HERE/'seal.json'))))
if __name__=='__main__':main()
