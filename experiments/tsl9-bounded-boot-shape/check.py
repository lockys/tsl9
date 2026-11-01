"""Bounded ID2580 BOOT and APP shape check; no excluded APP payload read."""
from pathlib import Path
import json
import hashlib

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
    0x20e2: '21630283',
}
if boot.stat().st_size < max(pc - 0x1000 + len(bytes.fromhex(hexbytes)) for pc,hexbytes in anchors.items()):
    raise ValueError('BOOT shorter than checked windows')
with boot.open('rb') as stream:
    for pc, hexbytes in anchors.items():
        expected=bytes.fromhex(hexbytes)
        stream.seek(pc - 0x1000)
        if stream.read(len(expected)) != expected:
            raise ValueError('Selected BOOT anchor differs at '+hex(pc))
    stream.seek(0x231e - 0x1000)
    end_handler = stream.read(62)
    if hashlib.sha256(end_handler).hexdigest() != '5aada9fcd13f973eb94a50f2abd909af7e4bdf233d9b34115023b7ce83fa0dbb':
        raise ValueError('Candidate BOOT end-handler window changed')
pages = []
reset_windows = []
for image in (official, candidate):
    if image.stat().st_size != 76800:
        raise ValueError('APP image size differs')
    # Two explicit allowed windows; never read either excluded APP range.
    with image.open('rb') as stream:
        pages.append(stream.read(1024))
        stream.seek(0x186aa - 0x8000)
        reset_windows.append(stream.read(0x8a))
if pages[0] != pages[1] or hashlib.sha256(pages[0]).hexdigest() != '90f03cc6687486011333937ddecd72767f464560f8039d66114ecf9e30250fe0':
    raise ValueError('APP initial page differs')
if reset_windows[0] != reset_windows[1] or hashlib.sha256(reset_windows[0]).hexdigest() != '9507502c874a03e2c64a28b186a1f56aba9e85c9989dbf0cc053dabc4045bb4d':
    raise ValueError('APP reset window differs')
def jal_target(instruction, pc):
    word = int.from_bytes(instruction, 'little')
    if word & 0x7f != 0x6f or (word >> 7) & 31:
        raise ValueError('Expected JAL zero')
    delta = (((word >> 31) & 1) << 20) | (((word >> 21) & 0x3ff) << 1) | (((word >> 20) & 1) << 11) | (((word >> 12) & 0xff) << 12)
    return pc + (delta - (1 << 21) if delta & (1 << 20) else delta)
if jal_target(pages[0][:4], 0x8000) != 0x186aa or jal_target(reset_windows[0][-4:], 0x18730) != 0x40000:
    raise ValueError('APP entry or resident handoff changed')
page_count = 76800 // 1024
assert 76800 % 1024 == 0 and page_count == 75
assert all(0 <= index <= 95 and len(index.to_bytes(2, 'big')) + 1024 == 1026 for index in range(page_count))
print(json.dumps({'boot_anchors':len(anchors),'boot_end_window_matches':True,'candidate_boot_app_jump':'0x8000','initial_page_matches':True,'reset_window_matches':True,'entry':'0x186aa','resident_handoff':'0x40000','pages':page_count,
                  'page_range':[0,74],'candidate_boot_bound':[0,95],
                  'excluded_app_read':False,'installed_boot_identified':False,'hardware_tested':False}))
