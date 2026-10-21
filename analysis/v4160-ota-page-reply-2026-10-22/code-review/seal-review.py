#!/usr/bin/env python3
"""Create once; generated build trees and executable archives are excluded."""
import hashlib
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
MEMBERS=('README.md','readme.zh-TW.md','readme.en.md','expected-effects.c','run-effects.py','run-effects.sh','check-review.py','check-review.sh','selected-receipts.json','seal-review.py')
def main():
    output=HERE/'seal.json'
    if output.exists():raise ValueError('Create-only review seal already exists')
    if (HERE/'README.md').read_bytes()!=(HERE/'readme.zh-TW.md').read_bytes():raise ValueError('Default README must equal full Traditional Chinese guide')
    result={'schema':'ID2966-page-reply-independent-host-code-review-v1','members':{name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in MEMBERS},'generated_builds_published':False,'native_proof_claimed':False}
    output.write_bytes((json.dumps(result,indent=2)+'\n').encode('utf-8'));print(json.dumps({'members':len(MEMBERS),'seal_sha256':hashlib.sha256(output.read_bytes()).hexdigest()}))
if __name__=='__main__':main()
