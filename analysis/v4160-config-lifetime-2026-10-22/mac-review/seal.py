"""Create-only original helper-footprint evidence closure."""
from pathlib import Path
import hashlib
import json
HERE=Path(__file__).resolve().parent
NAMES=('check.py','check.sh','capture.py','ledger.json','selected.json','README.md','readme.zh-TW.md','readme.en.md','seal.py')
def main():
    path=HERE/'seal.json'
    if path.exists():raise ValueError('Already sealed; do not mutate original review')
    selected=json.loads((HERE/'selected.json').read_bytes());m=selected['metadata'];a=selected['actual_firmware'];e=selected['actual_firmware_and_ELF']
    assert m['passed'] and m['metadata_only'] and not m['actual_original_firmware_read'] and not m['actual_helper_ELF_view_read']
    assert a['passed'] and not a['metadata_only'] and a['actual_original_firmware_read'] and not a['actual_helper_ELF_view_read']
    assert e['passed'] and e['actual_original_firmware_read'] and e['actual_helper_ELF_view_read']
    for item in (a,e):
        assert item['raw_controls']==4 and all(x['rejected'] for x in item['controls'])
    for item in (m,a,e):
        assert item['helper_local_footprint_obligation_resolved']
        assert item['facts']['helper_explicit_GPR_writes']==[13,14,15]
        assert item['facts']['nested_calls']==0 and item['facts']['caller_copy_write_SP_offsets']==[40,45]
        assert item['facts']['entire_caller_slice_explicitly_writes_staCB'] is False
        for k in ('whole_config_zero_lifetime_proved','earlier_resident_callee_effects_proved','hardware_MAC_or_UID_value_read','whole_ELF_provenance_replayed','full_original_ABI_proved','whole_OTA_proved','new_BIN_generated','compiler_or_HOST_run','target_execution','ISA_emulation','hardware','network'):assert item[k] is False,k
    assert (HERE/'README.md').read_bytes()==(HERE/'readme.zh-TW.md').read_bytes()
    members={}
    for n in NAMES:
        data=(HERE/n).read_bytes();data.decode('utf-8');assert b'\r' not in data and data.endswith(b'\n') and not data.endswith(b'\n\n'),n
        members[n]=hashlib.sha256(data).hexdigest()
    with path.open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(dict(schema='TSL9-local-helper-footprint-seal-v1',members=members,generated_build_members=False,whole_config_lifetime_proved=False),indent=2)+'\n')
    print(json.dumps(dict(passed=True,members=len(members),seal_sha256=hashlib.sha256(path.read_bytes()).hexdigest())))
if __name__=='__main__':main()
