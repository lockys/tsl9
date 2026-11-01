"""Bounded ID2580 BOOT and APP shape check; no excluded APP payload read."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[2]
folder = root / 'firmware-downloads/legacy-options-2026-10-20/BINs'
boot = folder / 'ID-2580-V1.0.00-decoded.bin'
official = folder / 'ID-2966-V4.1.60-decoded.bin'
candidate = root / 'artifacts/offline-images/ID2966-V4.1.60-tx-integrated/NOT-FLASH-VALIDATED-tx-integrated.bin'
anchors = {
    0x2202: '83c7b108', 0x2208: '93072040', 0x220c: 'e39bf6fc',
    0x2210: '83471600', 0x2214: '03440600', 0x2218: '3787fff7',
    0x222a: 'b7070200', 0x222e: '93870702', 0x2238: 'e167',
    0x223c: '938707f0', 0x2240: 'e3e1e7fa', 0x25f4: '83c70700',
    0x25f8: '1307f006', 0x25fc: '6307f700',
}
if boot.stat().st_size < max(pc - 0x1000 + len(bytes.fromhex(hexbytes)) for pc,hexbytes in anchors.items()):
    raise ValueError('BOOT shorter than checked windows')
with boot.open('rb') as stream:
    for pc, hexbytes in anchors.items():
        expected=bytes.fromhex(hexbytes)
        stream.seek(pc - 0x1000)
        if stream.read(len(expected)) != expected:
            raise ValueError('Selected BOOT anchor differs at '+hex(pc))
for image in (official, candidate):
    if image.stat().st_size != 76800:
        raise ValueError('APP image size differs')
    # Only APP offset 0 is read; the excluded APP regions are never opened as data.
    with image.open('rb') as stream:
        if stream.read(1) != bytes([0x6f]):
            raise ValueError('APP first byte differs')
page_count = 76800 // 1024
assert 76800 % 1024 == 0 and page_count == 75
assert all(0 <= index <= 95 and len(index.to_bytes(2, 'big')) + 1024 == 1026 for index in range(page_count))
print(json.dumps({'boot_anchors':len(anchors),'app_first_byte_matches':True,'pages':page_count,
                  'page_range':[0,74],'candidate_boot_bound':[0,95],
                  'excluded_app_read':False,'installed_boot_identified':False,'hardware_tested':False}))
