"""Verify bounded original SPI initialization instruction windows."""
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = {
    0x1716c: ('9307401002c602ca2317f1009307002002cc231bf100c147231cf1006c009d47'
              '37350140231ef10002c8ef20e052854537350140ef20e057'),
    0x196c4: ('035705008d679387070483d625007d8f83d70500d58f83d64500d58f83d66500'
              'd58f83d68500d58f83d6a500d58f83d6c500d58f83d6e500d58fd98f2310f500'
              '0357c501fd779387f77ff98f231ef50083d705012318f50082808357050091c5'
              '93e707042310f5008280c207c18393f7f7fbc207c183fdb7'),
}
with image.open('rb') as stream:
    for address, hex_bytes in windows.items():
        expected = bytes.fromhex(hex_bytes)
        stream.seek(address - 0x8000)
        if stream.read(len(expected)) != expected:
            raise SystemExit('Original SPI instruction window changed')
fields = (0, 0x104, 0, 0, 0, 0x200, 0x10, 0, 7)
combined = 0
for field in fields[:8]:
    combined |= field
if combined != 0x314 or ((0xffff & 0x3040) | combined | 0x40) != (0x3000 | 0x354):
    raise SystemExit('SPI bit merge changed')
print('SPI instruction windows and configuration bit merge verified; target not executed.')
