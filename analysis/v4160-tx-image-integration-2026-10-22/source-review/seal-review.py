"""Create-only source/metadata seal; generated build archives are excluded."""
import hashlib
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not (HERE/'seal.json').exists(),'Create-only immutable review'
    assert (HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes()
    selected=json.loads((HERE/'selected-results.json').read_bytes());assert set(selected)=={'c','cpp'}
    for r in selected.values():
        assert r['passed'] and r['actual_source_compile_provenance_replayed'] and r['actual_ABI_LOAD_image_replayed']
        assert r['source_provenance']['actual_commands']==67 and r['source_provenance']['actual_MD_rules']==45
        assert r['focused_actual_byte_controls']['actual_byte_mutations_rejected']==9 and r['focused_recipe_dependency_controls']['focused_recipe_dependency_controls']==14
    members={p.name:sha(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='seal.json'}
    for p in HERE.glob('*.md'):assert p.read_bytes().endswith(b'\n') and not p.read_bytes().endswith(b'\n\n'),'One Markdown EOF newline'
    result=dict(schema='ID2966-thirteen-image-independent-source-seal-v1',members=members,source_metadata_only=True,generated_build_artifacts_published=False,target_execution=False)
    with (HERE/'seal.json').open('xb') as f:f.write((json.dumps(result,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(dict(passed=True,members=len(members),seal_sha256=sha(HERE/'seal.json'))))
if __name__=='__main__':main()
