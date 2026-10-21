"""Create or verify this bounded inventory's immutable file snapshot."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
NAMES = ('scan.py', 'scan.sh', 'report.json', 'README.md', 'readme.zh-TW.md', 'readme.en.md', 'seal.py')
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--check', action='store_true')
a = p.parse_args()
if (HERE/'README.md').read_bytes() != (HERE/'readme.zh-TW.md').read_bytes():
    raise ValueError('Full Traditional Chinese README identity')
members = []
for name in NAMES:
    data = (HERE/name).read_bytes()
    if not data.endswith(b'\n') or data.endswith(b'\n\n') or b'\r' in data:
        raise ValueError('UTF8/LF/single EOF: '+name)
    data.decode('utf8')
    members.append(dict(path=name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
value = dict(schema='TSL9-literal-interior-inventory-seal-v1', passed=True, members=members,
             source_scope='literal U32LE carriers in three exact images only',
             computed_references_or_ROM_proved_absent=False, target_execution=False,
             ISA_emulation=False, hardware=False, network=False, new_BIN=False, OTA_ready=False)
payload = (json.dumps(value, indent=2)+'\n').encode('utf8')
destination = HERE/'seal.json'
if a.check:
    if destination.read_bytes() != payload:
        raise ValueError('Exact immutable inventory snapshot')
else:
    with destination.open('xb') as output:
        output.write(payload)
print(json.dumps(dict(passed=True, members=len(members), seal_sha256=hashlib.sha256(payload).hexdigest())))
