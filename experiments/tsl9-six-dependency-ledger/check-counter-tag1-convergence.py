"""Verify bounded original instruction windows; do not execute target code."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = {
    (0xae0e, 0x14e): 'f0178263a7827e6c63da36003011c01b1fd0141671f3abb1a0b7dfa9e587e6db',
    (0xaf4c, 0x30): '838a7e9c3276102dc1803012028735e498334cec16c7a3009ba5728d2095c28b',
    (0xb016, 0x1c): 'a2edf735aab5fb410573a0c26dcc3b0b676ad00b3414cc59484a91676999205e',
    (0x1069e, 0x20): '539d49112d335287022ff904bfeaaaabda1a644ea54621fe832160fed5758588',
}
with image.open('rb') as stream:
    for (address, size), expected in windows.items():
        stream.seek(address - 0x8000)
        if hashlib.sha256(stream.read(size)).hexdigest() != expected:
            raise SystemExit('Original instruction window changed')
print('Tag 1 convergence windows verified; target execution unverified.')
