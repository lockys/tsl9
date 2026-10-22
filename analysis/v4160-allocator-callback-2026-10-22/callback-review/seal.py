"""Create-only bounded callback-owner source closure."""
from pathlib import Path
import hashlib
import json
HERE=Path(__file__).resolve().parent
NAMES=('check.py','check.sh','capture.py','ledger.json','selected.json','README.md','readme.zh-TW.md','readme.en.md','seal.py')
def main():
    path=HERE/'seal.json'
    if path.exists():raise ValueError('Already sealed; preserve immutable evidence')
    selected=json.loads((HERE/'selected.json').read_bytes());m=selected['metadata'];a=selected['actual_files']
    assert m['passed'] and m['metadata_only'] and not m['actual_original_firmware_read'] and m['actual_candidate_sources_read']==0
    assert a['passed'] and not a['metadata_only'] and a['actual_original_firmware_read'] and a['actual_candidate_sources_read']==2
    assert (a['actual_init_prefix_bytes_per_candidate'],a['actual_init_prefix_rows_per_candidate'],a['actual_zero_helper_bytes_per_candidate'],a['actual_zero_helper_rows_per_candidate'],a['actual_initializer_tail_bytes_per_candidate'])==(114,41,30,9,8)
    assert a['adjacent_callback_load_pairs_per_candidate']==12 and a['raw_controls']==8 and all(x['rejected'] for x in a['controls'])
    assert m['conditional_config_copy_owner_confirmed'] and a['conditional_config_copy_owner_confirmed']
    for k in ('callback_function_identity_proved','callback_lifetime_proved','installed_resident_identity_proved','ambient_A2_independence_proved','whole_ROM_reference_absence_proved','App_config_actually_zero_proved','full_original_ABI_proved','new_provider_or_BIN_generated','compiler_or_HOST_run','target_execution','ISA_emulation','network','hardware'):
        assert m[k] is False and a[k] is False,k
    assert (HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes()
    members={}
    for n in NAMES:
        b=(HERE/n).read_bytes();b.decode('utf-8');assert b'\r' not in b and b.endswith(b'\n') and not b.endswith(b'\n\n'),n
        members[n]=hashlib.sha256(b).hexdigest()
    with path.open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(dict(schema='TSL9-conditional-callback-owner-seal-v1',members=members,generated_build_members=False,installed_identity_proved=False),indent=2)+'\n')
    print(json.dumps(dict(passed=True,members=len(members),seal_sha256=hashlib.sha256(path.read_bytes()).hexdigest())))
if __name__=='__main__':main()
