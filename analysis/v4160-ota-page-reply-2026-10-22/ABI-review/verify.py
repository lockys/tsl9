#!/usr/bin/env python3
"""Default metadata-only seal verification; never replay archived build artifacts."""
import hashlib
import json
from pathlib import Path

def main():
    here=Path(__file__).resolve().parent
    seal=json.loads((here/'seal.json').read_text(encoding='utf-8'))
    if seal.get('schema')!='TSL9-reply-ABI-review-seal-v1':raise ValueError('Known independent ABI seal schema')
    seen=set()
    for member in seal['files']:
        path=(here/member['path']).resolve()
        if not path.is_relative_to(here) or path==here/'seal.json' or member['path'] in seen:raise ValueError('Unique bounded source/metadata seal member')
        seen.add(member['path']);raw=path.read_bytes()
        if len(raw)!=member['bytes'] or hashlib.sha256(raw).hexdigest()!=member['sha256']:raise ValueError('Sealed member changed: '+member['path'])
    print(json.dumps({'passed':True,'mode':'metadata-only','members':len(seen),'actual_build_artifact_replay':False,'target_execution':False,'hardware_or_OTA_admitted':False}))
if __name__=='__main__':main()
