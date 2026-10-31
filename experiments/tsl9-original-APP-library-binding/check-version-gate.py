"""Verify bounded APP version gate and candidate comparator evidence."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
sources = {
    'app': (root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin', 0x8000),
    'candidate': (root / 'analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin', 0x40000),
}
windows = [
    ('app', 0x199e2, 0x28, 'bb6128747c5ea4994b05006f5043e89e857e396404649742e49760ae411fcba0'),
    ('app', 0x19ad2, 0x20, 'fcd5faa670571cfe6360a8bb5428748f437ee38af7272013882a8dd807275104'),
    ('candidate', 0x4003c, 4, '57f4636af1c7810c89be5b737be62e4b67a56533cc07ccdf6ccc2c16fe5a6720'),
    ('candidate', 0x406b2, 72, 'a9dbd2b47ccefe55ab45f0b4e5a073d7aeb00f42dbe503191a75b6b66efff3aa'),
]
for source, address, size, expected in windows:
    path, base = sources[source]
    with path.open('rb') as stream:
        stream.seek(address - base)
        if hashlib.sha256(stream.read(size)).hexdigest() != expected:
            raise SystemExit('Original or candidate window changed')
print('Version gate and candidate comparator windows verified; target not executed.')
