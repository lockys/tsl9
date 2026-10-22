"""Metadata/source check; no generated native archives are opened by default."""
import argparse,json
from pathlib import Path
import review
def check(root):
    review.need((review.HERE/'seal.json').is_file(),'Closed source/metadata bundle required')
    review.closed();review.need((review.HERE/'README.md').read_bytes()==(review.HERE/'readme.zh-TW.md').read_bytes(),'Full Traditional Chinese default')
    result=review.inspect(root);review.need(result['metadata_only'] and not result['actual_native_artifacts_read'],'Honest default scope')
    result['sealed_members']=len(review.read(review.HERE/'seal.json')['members']);return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path);a=p.parse_args();print(json.dumps(check(a.project_root)))
