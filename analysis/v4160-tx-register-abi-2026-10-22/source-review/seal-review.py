#!/usr/bin/env python3
"""Create-only source constraints; no component implementation is admitted."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
MEMBERS=('check-source.py','check-source.sh','source-review.json','README.md','readme.zh-TW.md','readme.en.md','seal-review.py')
def main():
    target=HERE/'seal.json'
    if target.exists():raise ValueError('Already sealed')
    if (HERE/'README.md').read_bytes()!=(HERE/'readme.zh-TW.md').read_bytes():raise ValueError('TW default identity')
    selected=json.loads((HERE/'source-review.json').read_bytes())
    if len(selected['raw_boundary_controls'])!=7 or not all(r['rejected'] for r in selected['raw_boundary_controls']):raise ValueError('Seven original boundary controls')
    if len(selected['adapter_source_controls'])!=5 or len(selected['selected_actual_pre_motion_adapters'])!=2 or any(not r['passed'] or len(r['actual_code_byte_controls'])!=5 for r in selected['selected_actual_pre_motion_adapters']):raise ValueError('Source controls plus both actual adapter subsets and byte controls')
    data={'schema':'TSL9-TX-typed-source-entry-frame-constraints-v1','members':{n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in MEMBERS},'replacement_admitted':False,'generated_builds_published':False,'target_execution':False,'hardware':False,'OTA_ready':False}
    target.write_bytes((json.dumps(data,indent=2)+'\n').encode('utf-8'));print(json.dumps({'members':len(MEMBERS),'seal_sha256':hashlib.sha256(target.read_bytes()).hexdigest()}))
if __name__=='__main__':main()
