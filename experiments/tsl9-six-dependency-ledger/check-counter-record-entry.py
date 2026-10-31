"""Pin direct record-dispatch, checksum gate and source-update entry evidence."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = {
    (0x14d2e, 0x40): 'f4766d35621c0aaaa880c0e1f5fbdfcfd31d767ae5e9b25468f344f5a0815232',
    (0x14ed8, 0x50): '0f1b5df2f39a7a8efe659d497aad1546a71b3cb51adea780c76603f8f17959cf',
    (0x152dc, 0x18): '37eec0ffae5515f2c470cc48edfba3175e0aee2094c2ab27498e61e939d7f1f7',
    (0xb036, 0x4c): '8a7ded4457aa77c56733facc56627dc9fbc1aed22f7147649d1666935ca7b502',
    (0x1069e, 0x22): 'e79f7c9c957f6fd415b1a69da830c13e13124a03d03c89d42b2aa92ffff84067',
    (0xae0e, 0x4c): 'e2288b607dbddd27061d8b5a88060d339344305b69b2bf783e8cc5d9bb0e09d3',
    (0x1a6bc, 4): '8589c7149ff9224ee9ceeadcf38882c882b6fa99bedeab17f3e1b580f6baea9c',
}
with image.open('rb') as stream:
    for (address, size), expected in windows.items():
        stream.seek(address - 0x8000)
        data = stream.read(size)
        if hashlib.sha256(data).hexdigest() != expected:
            raise SystemExit('Original instruction or table window changed')
        if address == 0x1a6bc:
            target = (0x1a6b8 + int.from_bytes(data, 'little', signed=True)) & 0xffffffff
            if target != 0x14d5e:
                raise SystemExit('Unexpected selector 1 target')
print('Counter record dispatch and checksum gate windows verified; target not executed.')
