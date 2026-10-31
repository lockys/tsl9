"""Check bounded original instruction and initializer evidence offline."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = {
    (0x1874a, 234): 'e0debe8b77025cfb56144045a0aa7524b7a2cd2ad0bd3daa2d880408ad9758f5',
    (0x18834, 174): '1fe76c3ddc25809287b5ebaf84cd508bcffeebc7b442eac36b33a38ab2f81e1e',
    (0x1908c, 18): '8a1f8aa217067a65d4a6cfa6420d03b423019f47471c699a98afc65062a01b0a',
    (0x19818, 96): '61848e7fb444d79939f528d95f493396aa250fdbb54a534b56741753c431cedb',
    (0x198ea, 20): '25455610a509c997fd56813fd8a286d8dc7ef793fbd8bdfb88c25c599e71b3f4',
}
with image.open('rb') as stream:
    for (address, size), expected in windows.items():
        stream.seek(address - 0x8000)
        if hashlib.sha256(stream.read(size)).hexdigest() != expected:
            raise SystemExit('Clock instruction window changed')
    stream.seek(0x1aba0 - 0x8000)
    if stream.read(1) != b'\x00':
        raise SystemExit('Clock shift-table entry changed')
pll_config = 0x00290000
cleared = 0xffc0ffff
fields = 0x003f0000
if cleared & fields or pll_config & fields != pll_config:
    raise SystemExit('PLL field mask changed')
if ((pll_config >> 16) & 1, (pll_config >> 17) & 1, (pll_config >> 18) & 15) != (1, 0, 10):
    raise SystemExit('PLL source, prescaler or multiplier fields changed')
if ((pll_config >> 18) & 15) + 2 != 12:
    raise SystemExit('Unexpected PLL field')
if 8000000 * 12 // 8 != 12000000:
    raise SystemExit('Unexpected conditional SCK arithmetic')
if 32000000 // 4 != 8000000 or (32000000 // 4) * 12 != 96000000:
    raise SystemExit('Unexpected documented candidate oscillator arithmetic')
usb_fields = set()
for initial in range(4):
    reg = (initial << 22) & 0xf8ff0000
    reg &= 0xff80ffff
    reg = (reg | 0x400) & 0xffc0ffff
    reg = (reg | pll_config) & 0xfffffffc | 2
    usb_fields.add((reg >> 22) & 3)
if usb_fields != {0, 2}:
    raise SystemExit('Unexpected conditional USB prescaler fields')
if ((0xffff3fff & 0x00c00000) != 0x00c00000 or
        (0x0000c000 & 0x00c00000) != 0 or
        ((0x0000c000 >> 14) & 3) != 3 or 96000000 // 8 != 12000000):
    raise SystemExit('Unexpected candidate ADC/USB preservation arithmetic')
print('Clock instruction windows and conditional arithmetic verified; target not executed.')
