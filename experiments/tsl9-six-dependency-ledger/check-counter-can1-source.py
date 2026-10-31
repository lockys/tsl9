"""Pin bounded CAN receive, ring, dispatch and checksum evidence."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = {
    (0x12c24, 0x2e): '64aa1fb9880d5d08e99eabe5babfd30acb92e1082bf3755ae1f880654f9f1992',
    (0x18d78, 0xa2): '80e48139a2196b615dfbb426e661884718999572702b200fc91d1d62a50c12c4',
    (0x12bc8, 0x5c): 'd3d9af9bcec8af13dfd424d3bfb2bd79f8fc3fd61308cb6ec0d7c18b1b78b13b',
    (0x12c86, 0x30): 'dec6a481783ed572c527a4b76612a36bbb58fb3bf7af82abe2c49ebb3b404f08',
    (0x12d78, 0x1a): '1b58b58aa72f90ce0b1cf31b81c0290eb922c8614a5da01f9cb0b1eb438a4cfe',
    (0xed00, 0x36): 'fbf7bb41f2d9f68ba60b4e856ca54d29755ce6782b62575b6d915a18157e5d1b',
}
with image.open('rb') as stream:
    for (address, size), expected in windows.items():
        stream.seek(address - 0x8000)
        if hashlib.sha256(stream.read(size)).hexdigest() != expected:
            raise SystemExit('Original instruction window changed')
if not all(0 < value < 2048 for value in (0x399, 0x39b)):
    raise SystemExit('Identifier comparison outside standard numerical range')
print('CAN receive, ring and checksum windows verified; target not executed.')
