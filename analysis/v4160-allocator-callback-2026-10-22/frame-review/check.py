"""Source/metadata validation only; actual firmware and generated artifacts require review.py."""
import argparse,json
from pathlib import Path
import review,source_delta
def check(root):
    root=Path(root).resolve(strict=True);review.need((review.HERE/'seal.json').is_file(),'Closed source/metadata seal');review.closed()
    refs=review.read(review.HERE/'reference-pins.json')
    for name,pin in refs.items():
        p=root/name
        if not p.is_file() and name.startswith('apk-analysis/tsl9-'):p=root/name.replace('apk-analysis/tsl9-','analysis/',1)
        review.need(p.is_file() and review.sha(p)==pin,'Pinned source/reference '+name)
    review.need((review.HERE/'README.md').read_bytes()==(review.HERE/'readme.zh-TW.md').read_bytes(),'Complete Traditional Chinese default')
    source_delta.inspect(root)
    return dict(passed=True,metadata_only=True,sealed_members=len(review.read(review.HERE/'seal.json')['members']),
        actual_original_firmware_read=False,actual_native_artifacts_read=False,actual_archive_replay=False,
        bounded_source_delta_checked=True,HOST_rerun=False,new_compile=False,target_execution=False,ISA_emulation=False,full_ABI_admitted=False)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path);a=p.parse_args();print(json.dumps(check(a.project_root)))
