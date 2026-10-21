#!/usr/bin/env python3
"""Create-only reviewed TX HOST evidence closure; generated builds excluded."""
import hashlib
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
MEMBERS=('expected-effects.c','run-effects.py','run-effects.sh','replay-controls.py','check-review.py','check-review.sh','selected-verification.json','README.md','readme.zh-TW.md','readme.en.md','seal-review.py')
def main():
    target=HERE/'seal.json'
    if target.exists():raise ValueError('Already sealed')
    if (HERE/'README.md').read_bytes()!=(HERE/'readme.zh-TW.md').read_bytes():raise ValueError('Default full Traditional Chinese identity')
    r=json.loads((HERE/'selected-verification.json').read_bytes())
    if len(r['independent'])!=2 or any(not v['actual_readonly_replay_passed'] or v['receipt_controls_rejected']!=10 for v in r['independent']):raise ValueError('Actual independent both-mode readback and controls required')
    result={'schema':'ID2966-TX-independent-HOST-review-seal-v1','members':{n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in MEMBERS},'generated_builds_published':False,'target_execution':False,'native_fixed_placement_admitted':False,'hardware':False,'OTA_ready':False}
    target.write_bytes((json.dumps(result,indent=2)+'\n').encode('utf-8'));print(json.dumps({'members':len(MEMBERS),'seal_sha256':hashlib.sha256(target.read_bytes()).hexdigest()}))
if __name__=='__main__':main()
