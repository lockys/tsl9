"""Verify bounded SPI filter path evidence; do not execute target code."""
import hashlib
import struct
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = {
    (0x12b82, 0x12): '3b436f0f2de215a5c82eed092b3e2833e39b12e44b59e11a9ad3240578d98961',
    (0x16dd4, 0x38): '986860b86812929c691ba1ccd2bd9099bb562ce0df5d74e7cd1e25ed18d6f49a',
    (0x16cc4, 0xe8): '9522255b0cd785c2fb07aaea6c96ace7a60bd80dce18f87f75aa5a3c48ed5155',
    (0x16a7c, 0x8c): '44ca48ec2799f182b3b758b8055a9ae95b7241dfbed7739361a86601a16e981e',
    (0x12bc8, 0x5c): 'd3d9af9bcec8af13dfd424d3bfb2bd79f8fc3fd61308cb6ec0d7c18b1b78b13b',
}
with image.open('rb') as stream:
    for (address, size), expected in windows.items():
        stream.seek(address - 0x8000)
        if hashlib.sha256(stream.read(size)).hexdigest() != expected:
            raise SystemExit('Original evidence window changed')
for word, expected in ((0x01450399, (0x399, 0x145)), (0x039b0370, (0x370, 0x39b))):
    if struct.unpack('<HH', struct.pack('<I', word)) != expected:
        raise SystemExit('Constant halfword encoding changed')
print('SPI filter path windows verified; hardware and resident contracts unverified.')
