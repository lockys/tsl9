"""Closed metadata/source validation only; generated artifacts require explicit review.py."""
import argparse,json
from pathlib import Path
import review,delta
def check(root):
    root=Path(root).resolve(strict=True);review.need((review.HERE/'seal.json').is_file(),'Closed object source/metadata seal');review.closed()
    for name,pin in review.read(review.HERE/'reference-pins.json').items():
        p=root/name
        if not p.is_file() and name.startswith('apk-analysis/tsl9-'):p=root/name.replace('apk-analysis/tsl9-','analysis/',1)
        review.need(p.is_file() and review.sha(p)==pin,'Pinned source/reference '+name)
    delta.inspect(root);review.need((review.HERE/'README.md').read_bytes()==(review.HERE/'readme.zh-TW.md').read_bytes(),'Full Traditional Chinese default')
    return dict(passed=True,metadata_only=True,sealed_members=len(review.read(review.HERE/'seal.json')['members']),bounded_source_delta_checked=True,
        actual_original_firmware_read=False,actual_native_artifacts_read=False,actual_archive_replay=False,
        HOST_rerun=False,new_compile=False,new_BIN=False,target_execution=False,ISA_emulation=False,full_ABI_admitted=False)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path);a=p.parse_args();print(json.dumps(check(a.project_root)))
