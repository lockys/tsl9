#!/usr/bin/env python3
"""Create-only closure after both public paths have been tested."""
import hashlib
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
MEMBERS = ('check-review.py', 'check-review.sh', 'seal-review.py', 'README.md', 'readme.zh-TW.md', 'readme.en.md', 'verification.json')
def main():
    out = HERE / 'seal.json'
    if out.exists(): raise ValueError('Already sealed')
    result = json.loads((HERE / 'verification.json').read_text(encoding='utf-8'))
    if not (result['default']['passed'] and result['actual']['passed'] and result['actual']['actual_archived_carriers_replayed'] == 2): raise ValueError('Preseal public default and both actual carriers required')
    if (HERE / 'README.md').read_bytes() != (HERE / 'readme.zh-TW.md').read_bytes(): raise ValueError('TW default identity')
    data = {'schema': 'ID2966-TX-source-review-json-shape-correction-v2', 'members': {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in MEMBERS}, 'old_source_review_unchanged': True, 'generated_builds_published': False}
    out.write_bytes((json.dumps(data, indent=2) + '\n').encode('utf-8'))
    print(json.dumps({'members': len(MEMBERS), 'seal_sha256': hashlib.sha256(out.read_bytes()).hexdigest()}))
if __name__ == '__main__': main()
