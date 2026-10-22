"""Create-only closure of the complete candidate comparison-leaf review."""
from pathlib import Path
import hashlib
import json
HERE=Path(__file__).resolve().parent
NAMES=('check.py','check.sh','capture.py','ledger.json','selected.json','README.md','readme.zh-TW.md','readme.en.md','seal.py')
def main():
    path=HERE/'seal.json'
    if path.exists():raise ValueError('Already sealed; preserve bytes')
    results=json.loads((HERE/'selected.json').read_bytes());m=results['metadata'];a=results['actual_sources']
    assert m['passed'] and m['metadata_only'] and not m['actual_original_firmware_read'] and m['actual_candidate_leaf_bodies_read']==0
    assert a['passed'] and not a['metadata_only'] and a['actual_original_firmware_read']
    assert (a['actual_candidate_leaf_bodies_read'],a['actual_caller_prefixes_read'],a['actual_existing_fill_bodies_rechecked'],a['raw_controls'])==(2,2,2,8)
    assert all(x['rejected'] for x in a['controls'])
    for r in (m,a):
        assert r['candidate_leaf_bytes']==62 and r['candidate_leaf_instructions']==19 and r['explicit_GPR_destinations']==[10,13,14,15]
        assert r['normal_return_values']==[0,1] and r['null_or_zero_length_return']==0
        assert r['full_A1_vs_LBU_comparison_confirmed'] and r['conditional_local_S1_SP_and_config52_preservation_confirmed']
        for k in ('installed_resident_identity_proved','App_branch_reachability_proved','callback_lifetime_or_live_zero_proved','full_original_ABI_proved','complete_initializer_continuation_proved','new_provider_or_BIN_generated','compiler_or_HOST_run','target_execution','ISA_emulation','network','hardware'):assert r[k] is False,k
    assert (HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes()
    members={}
    for n in NAMES:
        b=(HERE/n).read_bytes();b.decode('utf-8');assert b'\r' not in b and b.endswith(b'\n') and not b.endswith(b'\n\n'),n
        members[n]=hashlib.sha256(b).hexdigest()
    with path.open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(dict(schema='TSL9-precopy-complete-leaf-seal-v1',members=members,generated_build_members=False,installed_identity_proved=False),indent=2)+'\n')
    print(json.dumps(dict(passed=True,members=len(members),seal_sha256=hashlib.sha256(path.read_bytes()).hexdigest())))
if __name__=='__main__':main()
