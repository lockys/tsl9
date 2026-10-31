"""Verify fixed instruction windows and RAM interval arithmetic offline."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = {
    0x89fa: '03d6a1081307f0406365c70413071600420741832395e10897360020938666fcb2962380f600',
    0x186de: '138501089745ff1f938565276377b500232005001105e36db5fe',
}
with image.open('rb') as stream:
    for address, hex_bytes in windows.items():
        expected = bytes.fromhex(hex_bytes)
        stream.seek(address - 0x8000)
        if stream.read(len(expected)) != expected:
            raise SystemExit('Pinned instruction window changed')

start, end = 0x2000b9d8, 0x2000b9d8 + 1040
zero_start, zero_end = 0x20004080, 0x2000c958
if not (zero_start <= start < end <= zero_end and end == 0x2000bde8):
    raise SystemExit('Unexpected buffer/reset intersection')
for offset, width in [(138, 2), (142, 2), (156, 1), (165, 1)]:
    field = 0x20004000 + offset
    if not zero_start <= field < field + width <= zero_end:
        raise SystemExit('Parser field outside reset range')
if not (0x20008000 < start and end <= 0x2000c000 and zero_end > 0x2000c000):
    raise SystemExit('Unexpected candidate RAM bounds')

def receipt(relative, expected):
    data = (root / relative).read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise SystemExit('Reviewed receipt changed')
    return json.loads(data)

clock = receipt('experiments/tsl9-clock-reset-noninterference/verification-v1.json',
                '58f27386453934c0bcb0e4835d89b5fe10f915802a4855ac448f14401c3a9cb2')
bootstrap = receipt('experiments/tsl9-resident-slot2-startup/evidence-v1.json',
                    '747690c800bd9fdeae4fbd0cdb91edc9cb99fb89f5269e5e09d0c4ccbc713576')
if not clock['passed'] or not clock['normal_return_preserves_GP_SP_RA']:
    raise SystemExit('Clock receipt does not establish its return contract')
writes = [(address, address + 4) for address in clock['explicit_store_addresses']]
writes += [(item['destination'], item['destination'] + 4) for item in bootstrap['slot_stores']]
writes += [(bootstrap['seed']['destination'], bootstrap['seed']['end_exclusive'])]
for key in ('first_copy', 'second_copy'):
    item = bootstrap[key]
    writes.append((item['destination'], item['last_destination_word_inclusive'] + 4))
writes.append((bootstrap['zero']['start'], bootstrap['zero']['last_word_inclusive'] + 4))
writes.append((0x2000fff0, 0x20010000))  # Candidate loader's conservative frame.
watched = [(start, end)] + [(0x20004000 + offset, 0x20004000 + offset + width)
                             for offset, width in [(138, 2), (142, 2), (156, 1), (165, 1)]]
if any(a < d and c < b for a, b in writes for c, d in watched):
    raise SystemExit('An explicit write overlaps watched ingress state')
print('Ingress store and reset/RAM/bootstrap bounds verified; target not executed.')
