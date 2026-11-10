"""Pin source bytes; mutations test integrity, not instruction semantics."""
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin'
HEADER = ROOT / 'analysis/wch-resident-candidate-2026-10-21/original-dec2023/wchble_rom.h'
FULL = '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'
SDK = '647a185941fedeb6ba16d544d9bca91a6f53219bb649a5513b59abeb21a9a94c'
WINDOWS = {
    (0x144a, 0x14c8): 'df22e14015b51fe4209a7ae1d63f8d62303f86f2e9bf74336f14cd186708f8a8',
    (0x1550, 0x163c): 'e8902960611e8267815b56251a98fa0d37fde2c331236f1305196c69d3ac8e8f',
}

def digest(data):
    return sha256(data).hexdigest()

def window_ok(data, start, end, expected):
    return len(data) >= end - 0x1000 and digest(data[start-0x1000:end-0x1000]) == expected

def main():
    data = IMAGE.read_bytes()
    sdk = HEADER.read_bytes()
    assert len(data) == 12288 and digest(data) == FULL
    assert digest(sdk) == SDK
    for (start, end), expected in WINDOWS.items():
        assert window_ok(data, start, end, expected)
        for pc in range(start, end):
            mutated = bytearray(data)
            mutated[pc-0x1000] ^= 1
            assert not window_ok(mutated, start, end, expected)
        assert not window_ok(data[:end-0x1000-1], start, end, expected)
    mutated = bytearray(sdk)
    mutated[len(mutated)//2] ^= 1
    assert digest(mutated) != SDK
    print('PASS: image, SDK header, 2 windows, every window byte mutated, 2 truncations, SDK mutation')

if __name__ == '__main__':
    main()
