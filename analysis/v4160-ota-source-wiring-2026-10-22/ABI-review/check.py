"""Closed source/metadata check only; does not replay generated archives."""
import argparse,json
from pathlib import Path
import machine as M
import review
def check(root):
    root=Path(root).resolve(strict=True);M.need((review.HERE/'seal.json').is_file(),'Closed independent metadata seal required');review.closed()
    M.need((review.HERE/'README.md').read_bytes()==(review.HERE/'readme.zh-TW.md').read_bytes(),'Traditional Chinese default is complete')
    refs=json.loads((review.HERE/'reference-pins.json').read_bytes())
    for name,pin in refs.items():
        path=root/name
        if not path.is_file() and name.startswith('apk-analysis/tsl9-'):path=root/name.replace('apk-analysis/tsl9-','analysis/',1)
        M.need(path.is_file() and M.sha(path)==pin,'Current immutable source/reference '+name)
    return dict(passed=True,metadata_only=True,sealed_members=len(review.read(review.HERE/'seal.json')['members']),
        current_source_pins_checked=len(refs),actual_full_image_artifacts_read=False,actual_original_firmware_read=False,
        actual_archive_replay=False,ROM_provider_proved=False,physical_free_storage_proved=False,full_ABI_admitted=False,
        HOST_rerun=False,target_execution=False,ISA_emulation=False,hardware_OTA_proved=False)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path);a=p.parse_args();print(json.dumps(check(a.project_root)))
