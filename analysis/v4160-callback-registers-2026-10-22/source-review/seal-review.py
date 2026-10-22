"""Create-only source/provenance review seal; no generated build binaries."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not (HERE/'seal.json').exists();assert (HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes()
    selected=json.loads((HERE/'selected-results.json').read_bytes());assert set(selected)=={'c','cpp'}
    for r in selected.values():
        assert r['passed'] and r['actual_native_source_compile_provenance_replayed'] and r['native_bytes']==624 and r['native_instructions']==223 and r['actual_native_control_count']==5
        assert r['after_register_frame_gate']['save_order_equal_original'] and not r['whole_original_ABI_admitted'] and not r['remaining_eight_bytes_owned_or_safe']
    for p in HERE.glob('*.md'):assert p.read_bytes().endswith(b'\n') and not p.read_bytes().endswith(b'\n\n')
    members={p.name:sha(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='seal.json'}
    with (HERE/'seal.json').open('xb') as f:f.write((json.dumps(dict(schema='ID2966-callback-registers-independent-source-seal-v1',members=members,source_metadata_only=True,generated_build_artifacts_published=False,target_execution=False),indent=2)+'\n').encode())
    print(json.dumps(dict(passed=True,members=len(members),seal_sha256=sha(HERE/'seal.json'))))
if __name__=='__main__':main()
