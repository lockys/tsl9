"""Create-only closure of the bounded static allocator review."""
import hashlib
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
NAMES=('check.py','check.sh','capture.py','source-ledger.json','selected.json','README.md','readme.zh-TW.md','readme.en.md','seal.py')

def main():
    path=HERE/'seal.json'
    if path.exists():raise ValueError('Already sealed; preserve bytes')
    selected=json.loads((HERE/'selected.json').read_bytes());m=selected['metadata'];a=selected['actual_files']
    assert m['passed'] and m['metadata_only'] and not m['actual_original_firmware_read'] and m['actual_candidate_bodies_read']==0
    assert a['passed'] and not a['metadata_only'] and a['actual_original_firmware_read'] and a['actual_candidate_bodies_read']==4
    assert a['reviewed_bytes_per_candidate']==196 and a['raw_operand_controls']==8 and all(x['rejected'] for x in a['controls'])
    for k in ('installed_resident_identity_proved','allocation_transitive_A2_independence_proved','pointer_nonescape_proved','dropping_ambient_arguments_authorized','full_original_ABI_proved','physical_Flash_or_NV_ownership_proved','new_provider_or_BIN_generated','compiler_or_HOST_run','target_execution','ISA_emulation','network','hardware'):
        assert m[k] is False and a[k] is False,k
    assert (HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes()
    members={}
    for n in NAMES:
        b=(HERE/n).read_bytes();b.decode('utf-8');assert b'\r' not in b and b.endswith(b'\n') and not b.endswith(b'\n\n'),n
        members[n]=hashlib.sha256(b).hexdigest()
    data=dict(schema='TSL9-slot70-bounded-static-review-seal-v1',members=members,generated_build_members=False,installed_identity_proved=False)
    with path.open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(data,indent=2)+'\n')
    print(json.dumps(dict(passed=True,members=len(members),seal_sha256=hashlib.sha256(path.read_bytes()).hexdigest())))
if __name__=='__main__':main()
