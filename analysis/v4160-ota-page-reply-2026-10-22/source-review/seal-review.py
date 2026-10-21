#!/usr/bin/env python3
"""Create the source-only closure once; never rewrite an existing seal."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MEMBERS = ('README.md', 'readme.zh-TW.md', 'readme.en.md', 'contracts.json',
           'retained-evidence.json', 'source-proof.json', 'source-proof.py',
           'check-review.py', 'check-review.sh', 'seal-review.py')

def main():
    target = HERE / 'seal.json'
    if target.exists():
        raise ValueError('Create-only source review seal already exists')
    if (HERE / 'README.md').read_bytes() != (HERE / 'readme.zh-TW.md').read_bytes():
        raise ValueError('Default README must equal full Traditional Chinese guide')
    result = {'schema': 'ID2966-page-reply-independent-source-seal-v1',
              'scope': 'original124B/50instructions; no rebuilt implementation admission',
              'members': {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in MEMBERS}}
    target.write_bytes((json.dumps(result, indent=2) + '\n').encode('utf-8'))
    print(json.dumps({'members': len(MEMBERS), 'seal_sha256': hashlib.sha256(target.read_bytes()).hexdigest()}))

if __name__ == '__main__':
    main()
