"""Seal/check completed source-plan text; this is not an artifact-build replay."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
NAMES = ('prepare_plan.py','report.json','README.md','readme.zh-TW.md','readme.en.md','seal.py')
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--check',action='store_true')
a = p.parse_args()
assert (HERE/'README.md').read_bytes() == (HERE/'readme.zh-TW.md').read_bytes()
members = []
for n in NAMES:
    raw = (HERE/n).read_bytes()
    assert b'\r' not in raw and raw.endswith(b'\n') and not raw.endswith(b'\n\n')
    members.append(dict(path=n,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
report = json.loads((HERE/'report.json').read_bytes())
assert report['passed'] and len(report['negative_controls']) == 6
seal = dict(passed=True,members=members,source_plan_only=True,native_compilation=False,
            full_image_integration=False,new_BIN=False,target_execution=False,hardware=False,network=False,OTA_ready=False)
raw = (json.dumps(seal,indent=2)+'\n').encode('utf8')
path = HERE/'seal.json'
if a.check:
    assert path.read_bytes() == raw
else:
    with path.open('xb') as out:
        out.write(raw)
print(json.dumps(dict(passed=True,members=len(members),sha256=hashlib.sha256(raw).hexdigest(),actual_object_replayed=False)))
