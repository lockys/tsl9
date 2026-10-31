"""Check bounded original instruction windows and mode word encodings."""
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = {
    0xd07c: ('97f7ff1f83c787ec6384a706411122c406c62a84ef302037a14763eba702'
             '83c72116a1e389476309f4029147630af4008547631ff400b707000193871750'
             '29a0b70700019387174017f7ff1f232af7e6b240224441018280b70700019387'
             '1720e5b722852244b240814541016f20b0738280'),
    0x10402: '03d501058280',
    0xffa4: ('83c7d112a5cf83c72116adcb83474500411106c6850722c403c7c1128946bd8b'
             '6308d70463eae60285466300d7042302f50081452a84efe07fd29387c11283c71700'
             'a301a40022852244b240fd17a386f11241016f2010218d46630ed7009146e317d7fc'
             '93e70704d9b793e70701c1b793e707026dbf93e7070855bf82802386a112a94791e1'
             '8547a386f1128280'),
}
with image.open('rb') as stream:
    for address, hex_bytes in windows.items():
        expected = bytes.fromhex(hex_bytes)
        stream.seek(address - 0x8000)
        if stream.read(len(expected)) != expected:
            raise SystemExit('Original instruction window changed')
for word, expected in [(0x01000501, [1, 5, 0, 1]),
                       (0x01000201, [1, 2, 0, 1]),
                       (0x01000401, [1, 4, 0, 1])]:
    if list(word.to_bytes(4, 'little')) != expected:
        raise SystemExit('Unexpected setter constant')
print('Mode setter instruction windows and constants verified; target not executed.')
