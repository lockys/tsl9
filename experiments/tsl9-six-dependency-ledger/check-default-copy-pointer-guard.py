"""Verify bounded original default-copy call and candidate helper windows."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
paths = {
    'app': (root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin', 0x8000),
    'candidate': (root / 'analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin', 0x40000),
}
windows = [
    ('app', 0x131a0, 0x16, '71be2c768196e96db7812aca79d39465c76a681f8dbaa85e6f9d8971d3406166'),
    ('candidate', 0x4004c, 4, '2a537908d67ca2b40a63f146b7610155b95b5bd88434ce28baf7f68dcec70918'),
    ('candidate', 0x405a2, 58, '558a82658cb54901945d4c2884f2e87e763f64d57c0cafa831307beb44ae0c36'),
]
for source, address, size, expected in windows:
    path, base = paths[source]
    with path.open('rb') as stream:
        stream.seek(address - base)
        if hashlib.sha256(stream.read(size)).hexdigest() != expected:
            raise SystemExit('Original or candidate instruction window changed')
if ((0 + 12) & 0xffffffff) != 12 or ((0xfffffff4 + 12) & 0xffffffff) != 0:
    raise SystemExit('Unexpected RV32 pointer arithmetic')
print('Default copy pointer and candidate windows verified; target not executed.')
