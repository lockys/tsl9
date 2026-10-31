"""Verify bounded evidence for the conditional SNV failure and APP gate chain."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
paths = {
    'app': (root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin', 0x8000),
    'candidate': (root / 'analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin', 0x40000),
}
windows = [
    ('app', 0x19ae2, 0x34, 'cd63753f4dfb338e6016cf3f07b06097314ca6739b4e7984710687de72176172'),
    ('candidate', 0x43d42, 0x1a, 'e034757ec9483538d602031fbd6af5c420a8d883abbc5f776da0a919bcf6234b'),
    ('candidate', 0x44022, 0xa0, '72f70ec3ff48430f0b198f914b6bd949fed111707b324a237e5af2f2f3b2ef11'),
]
for source, address, size, expected in windows:
    path, base = paths[source]
    with path.open('rb') as stream:
        stream.seek(address - base)
        if hashlib.sha256(stream.read(size)).hexdigest() != expected:
            raise SystemExit('Original or candidate instruction window changed')
data = (root / 'experiments/tsl9-original-SNV-Flash-binding/verification-v1.json').read_bytes()
if hashlib.sha256(data).hexdigest() != '440f3848555e285dbfee3d0533b7d2f27c0c55f8a39d0ff5632c29790865abcb':
    raise SystemExit('SNV receipt changed')
contract = json.loads(data)['contract']
if not (contract['passed'] and contract['buffer_allocation_failure_returns_1'] and
        contract['BLEInit_overwrites_nested_SNV_status'] and
        contract['BLE_success_does_not_prove_SNV_persistence']):
    raise SystemExit('SNV contract changed')
print('SNV failure and APP gate windows verified; target not executed.')
