"""Offline byte-window integrity check, not an ISA or control-flow verifier."""
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin'
FULL = '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'
WINDOWS = {
    (0x19fe, 0x1a16): '5031bb72e52da4fdba4fa6b9969bd6d0ae36de21dafa775088f139a4384a9eb5',
    (0x144a, 0x154e): 'a92231cfbc4853689ff9741a07d9a27abf95d7f58751bd594c231fa212c854e2',
    (0x1550, 0x1618): 'cec1ce025fc08db5f4aadccc8755ed9df7efa688e6ac81101caa14dd8737e80a',
    (0x2bd8, 0x2be0): 'f7082e0f70f336142105ce187c3fb0ed988f2a9156bf338834f077e009520201',
}

def digest(data):
    return sha256(data).hexdigest()

def valid_window(data, start, end, expected):
    return len(data) >= end - 0x1000 and digest(data[start-0x1000:end-0x1000]) == expected

def main():
    data = IMAGE.read_bytes()
    assert len(data) == 12288 and digest(data) == FULL
    for (start, end), expected in WINDOWS.items():
        assert valid_window(data, start, end, expected)
        for offset in (start - 0x1000, end - 0x1000 - 1):
            altered = bytearray(data)
            altered[offset] ^= 1
            assert not valid_window(altered, start, end, expected)
        assert not valid_window(data[:end - 0x1000 - 1], start, end, expected)
    altered = bytearray(data)
    altered[0] ^= 1
    assert digest(altered) != FULL
    print('PASS: pinned image, 4 windows, 8 mutations, 4 truncations, image mutation')

if __name__ == '__main__':
    main()
