#!/usr/bin/env python3
"""Close original source evidence once; no generated build objects are included."""
import hashlib
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
MEMBERS=('README.md','readme.zh-TW.md','readme.en.md','raw.py','proof.py','contracts.json','retained-disassembly.json','source-proof.json','check-review.py','check-review.sh','seal-review.py')
def main():
    target=HERE/'seal.json'
    if target.exists():raise ValueError('Create-only source review already closed')
    if (HERE/'README.md').read_bytes()!=(HERE/'readme.zh-TW.md').read_bytes():raise ValueError('Default README equals full Traditional Chinese guide')
    r={'schema':'ID2966-TX-original-source-review-seal-v1','members':{name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in MEMBERS},'build_objects_published':False,'C_CPP_implementation_admitted':False,'target_execution':False,'OTA_ready':False};target.write_bytes((json.dumps(r,indent=2)+'\n').encode('utf-8'));print(json.dumps({'members':len(MEMBERS),'seal_sha256':hashlib.sha256(target.read_bytes()).hexdigest()}))
if __name__=='__main__':main()
