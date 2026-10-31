"""Pin the counter source/update and reset instruction windows offline."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = {
    (0x81f8, 10): '2193a910fd0fc616e13077f45296fd206f645c31bde3808bb840419e7ffc8c89',
    (0xa0e2, 0x1c): 'cba0f680cafd8c838947df3691e60e032d00c00dbaaaf3a5055bf622a6a316e1',
    (0xa1f6, 6): 'a81a24177b40e32c1f798ea3643c08e1c9f1b05f2e4a798f248ed2fcf4e490ee',
    (0x186de, 26): '53e8753086d6a33d612f27e3f21393ac8c64e9603498c443023275973c3fa5a0',
    (0xaf4c, 0x38): '2f925d4d22df0778bc555eed128a98e8e0a1d4953e70672039cda002a71c9f8d',
    (0xb016, 0x20): '3cd2789ca94527427610ea18f7280119e0bf2492389ab72e1dcfe00ff7245890',
}
with image.open('rb') as stream:
    for (address, size), expected in windows.items():
        stream.seek(address - 0x8000)
        if hashlib.sha256(stream.read(size)).hexdigest() != expected:
            raise SystemExit('Original instruction window changed')
source = (0x81f8 + 0x20004000 - 782) & 0xffffffff
if source != 0x2000beea:
    raise SystemExit('Unexpected source address')
if not all(0x20004080 <= address < 0x2000c958 for address in (source, 0x200040aa, 0x200040b0)):
    raise SystemExit('Source or state outside reset range')
if any(((((b >> 2) + 13) & 15) <= 4) != (((b >> 2) & 15) in (3, 4, 5, 6, 7))
       for b in range(256)):
    raise SystemExit('Unexpected input field condition')
print('Counter source and reset windows verified; target not executed.')
