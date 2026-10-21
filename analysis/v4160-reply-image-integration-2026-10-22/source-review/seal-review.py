#!/usr/bin/env python3
"""Create-only source/provenance closure; excludes all generated build artifacts."""
import hashlib
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
MEMBERS=('README.md','readme.zh-TW.md','readme.en.md','source-inputs.py','provenance.py','countercases.py','check-review.py','check-review.sh','review-inputs.json','selected-receipts.json','results-c.json','results-cpp.json','seal-review.py')
def main():
    output=HERE/'seal.json'
    if output.exists():raise ValueError('Create-only independent review seal already exists')
    if (HERE/'README.md').read_bytes()!=(HERE/'readme.zh-TW.md').read_bytes():raise ValueError('Default README must equal full Traditional Chinese guide')
    result={'schema':'ID2966-twelve-image-independent-source-review-seal-v1','members':{name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in MEMBERS},'generated_build_artifacts_published':False,'default_actual_archive_replay':False,'compiler_alone_order_claimed':False,'target_execution':False,'OTA_ready':False}
    output.write_bytes((json.dumps(result,indent=2)+'\n').encode('utf-8'));print(json.dumps({'members':len(MEMBERS),'seal_sha256':hashlib.sha256(output.read_bytes()).hexdigest()}))
if __name__=='__main__':main()
