"""Create-only original-source seal after actual checks; no build archives."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not (HERE/'seal.json').exists()
    r=json.loads((HERE/'verification.json').read_bytes());assert r['passed'] and r['raw_instructions']==217 and r['raw_semantic_controls_rejected']==26 and r['actual_original_objects_replayed']==2 and not r['actual_native_or_HOST_replayed']
    assert (HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes()
    for p in HERE.glob('*.md'):assert p.read_bytes().endswith(b'\n') and not p.read_bytes().endswith(b'\n\n')
    members={p.name:sha(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='seal.json'}
    with (HERE/'seal.json').open('xb') as f:f.write((json.dumps(dict(schema='ID2966-event-callback-original-source-seal-v1',members=members,source_metadata_only=True,generated_build_archives_published=False,target_execution=False),indent=2)+'\n').encode('utf-8'))
    print(json.dumps(dict(passed=True,members=len(members),seal_sha256=sha(HERE/'seal.json'))))
if __name__=='__main__':main()
