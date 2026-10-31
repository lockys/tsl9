"""Pin bounded original windows and check selector/address arithmetic offline."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = {
    (0x1316a, 0x4c): 'df7eea710b3be61f7abb6cc47c7d07f5b0335a914f6d7f210716f433112a16f8',
    (0xf8ae, 0x34): 'd83d62f346c1f19fb17073fe7958e55aafadcd754ee5ad4c623f46ccf5b3a4b4',
    (0xf9ec, 0x38): 'ac00cb045c6e739e2e14595f85dedff3ffe3ab7f677ab934ee9119f43d98031c',
    (0x1ab50, 0x10): '5b9c6b07c63dcca91970eee925a1457ddf31a8edaff20dfdd6e0f3a6b4d10096',
}
excluded = ((0x14056, 0x14c8a), (0x1a69c, 0x1a6a0))
with image.open('rb') as stream:
    for (start, size), digest in windows.items():
        if any(start < end and start + size > begin for begin, end in excluded):
            raise SystemExit('Refusing excluded window')
        stream.seek(start - 0x8000)
        data = stream.read(size)
        if hashlib.sha256(data).hexdigest() != digest:
            raise SystemExit('Original window changed')
        if start == 0x1ab50:
            dispatch, threshold = data[:8], data[8:]
sources = {
    'src/native/startup/settings_defaults.c': '00bdebdf9aec6a6ddd188de9ec0822a2a04b76ab2b87e02585035ae5c892779f',
    'src/native/receive/remaining_record_dispatch.c': '1e5295e0aeefc3da266d48aed042822a9b8a9f76ab52c7cdbdcd72fa308c7b20',
    'src/native/receive/record_dispatch_tables.c': 'd059365ee0f705885b74d8ff3c5cc6a658211b372a83fb282d68cc71cd017ea1',
    'src/native/receive/runtime_service_links.c': '74f97408b18c5d0f3b46dd3ea31ea352debd3c03de66ec291d79f25541c798c8',
}
for name, digest in sources.items():
    if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
        raise SystemExit('Annotated source changed')
if dispatch != bytes((0, 0, 5, 10, 20, 31, 0, 0)):
    raise SystemExit('Unexpected dispatch table')
if threshold != bytes((255, 51, 76, 102, 127, 153, 178, 204)):
    raise SystemExit('Unexpected threshold table')
if any(x > 31 for x in dispatch) or sum(bool(x & 0xe0) and bool(x & 7) for x in range(256)) != 196:
    raise SystemExit('Unexpected selector arithmetic')
if [0x1ab48 + 2 * i for i in range(4, 12)] != list(range(0x1ab50, 0x1ab60, 2)):
    raise SystemExit('Unexpected halfword overlap')
print('Settings selector windows and arithmetic verified; target not executed.')
