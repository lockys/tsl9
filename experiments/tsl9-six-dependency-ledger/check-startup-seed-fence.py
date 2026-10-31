"""Pin candidate seed-copy and first RAM-helper call windows; do not execute them."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin'
source = root / 'experiments/tsl9-resident-slot2-startup/resident_slot2_startup.c'
if hashlib.sha256(source.read_bytes()).hexdigest() != 'c003ee916a75750c99289f98592e8df74d2fe47d6d22650c99954dd1f5d4c37a':
    raise SystemExit('Candidate annotated startup source changed')
windows = ((0x6de7e,0x44,'98fe32a0b24638e9f678c2112dbae4fa05ad6e45d2a9fb84bedb67c3831880b0'),
           (0x6de0c,0x46,'0c73bc66988cfdf20e82fa7bb732df5195b596cf195629e15704299fadada263'),
           (0x40280,0x30,'1b443f8c3926fac2d65fda618f0ead0c9d2f50cafe5b0ff9c72eb030c13fd5a8'))
with image.open('rb') as f:
    for address,size,expected in windows:
        f.seek(address-0x40000)
        data=f.read(size)
        if hashlib.sha256(data).hexdigest()!=expected:
            raise SystemExit('Candidate startup window changed')
        if address == 0x40280:
            continue
        pos=0
        while pos<len(data):
            n=4 if data[pos]&3==3 else 2
            if pos+n>len(data):
                raise SystemExit('Truncated instruction')
            if n==4 and data[pos:pos+4]==bytes.fromhex('0f100000'):
                raise SystemExit('Unexpected FENCE.I in startup window')
            pos+=n
if 0x20000040-0x20000010 != 48 or 0x402b0-0x40280 != 48:
    raise SystemExit('Seed copy range changed')
print('Candidate seed and first RAM-helper windows verified; target not executed.')
