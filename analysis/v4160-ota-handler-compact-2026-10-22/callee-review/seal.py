"""Create-only bounded source/metadata seal; no build binaries."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not (HERE/'seal.json').exists()
    assert (HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes()
    r=json.loads((HERE/'selected-results.json').read_bytes());assert set(r)=={'metadata','actual','actual_D_references'}
    assert r['metadata']['passed'] and r['metadata']['metadata_only'] and not r['metadata']['actual_original_firmware_read'] and r['metadata']['actual_candidate_source_bodies_read']==0
    for name in ('actual','actual_D_references'):
        x=r[name];assert x['passed'] and not x['metadata_only'] and x['actual_original_firmware_read'] and x['actual_candidate_source_bodies_read']==2
        assert (x['App_instruction_rows'],x['candidate_copy_rows'],x['raw_operand_controls'])==(48,18,6)
        assert not x['dropping_ambient_args_authorized'] and not x['installed_resident_identity_proved'] and not x['transitive_original_ABI_proved']
    for p in HERE.glob('*.md'):assert p.read_bytes().endswith(b'\n') and not p.read_bytes().endswith(b'\n\n')
    members={p.name:sha(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='seal.json'}
    with (HERE/'seal.json').open('xb') as f:f.write((json.dumps(dict(schema='ID2966-OTA-compact-bounded-callee-seal-v1',members=members,source_metadata_only=True,generated_build_artifacts_published=False,installed_resident_identity_proved=False,target_execution=False),indent=2)+'\n').encode('utf-8'))
    print(json.dumps(dict(passed=True,members=len(members),seal_sha256=sha(HERE/'seal.json'))))
if __name__=='__main__':main()
