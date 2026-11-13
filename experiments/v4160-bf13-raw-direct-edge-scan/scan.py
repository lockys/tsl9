#!/usr/bin/env python3
"""Offline raw JAL-pattern inventory; no instruction-boundary inference."""
import hashlib
from pathlib import Path
import sys
from typing import NamedTuple

BASE = 0x8000
SIZE = 76800
SHA256 = "0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667"
BIN = (Path(__file__).resolve().parents[2] / "firmware-downloads" /
       "legacy-options-2026-10-20" / "BINs" / "ID-2966-V4.1.60-decoded.bin")
TARGETS = frozenset((0xbd5a, 0xbd64))


class Hit(NamedTuple):
    offset: int
    word: int
    rd: int
    displacement: int
    target: int


# Raw patterns, not a list of proven callers. Exact snapshot detects drift in
# either the scanner or the hit set, including unexpected additional matches.
EXPECTED = (
    Hit(0x6d74, 0xfe7fc0ef, 1, -12314, 0xbd5a),
    Hit(0xde5a, 0xf0bf50ef, 1, -41206, 0xbd64),
    Hit(0xde70, 0xeebf506f, 0, -41238, 0xbd5a),
    Hit(0xde80, 0xedbf506f, 0, -41254, 0xbd5a),
    Hit(0xde90, 0xecbf506f, 0, -41270, 0xbd5a),
)


def check_pin(data):
    if len(data) != SIZE or hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError("BIN length or SHA-256 does not match pin")


def scan(data, base, targets):
    """Examine every complete little-endian 32-bit window at even offsets."""
    hits = []
    examined = 0
    for offset in range(0, len(data) - 3, 2):
        examined += 1
        word = int.from_bytes(data[offset:offset + 4], "little")
        if word & 0x7f != 0x6f:
            continue
        immediate = (((word >> 31) & 1) << 20 |
                     ((word >> 21) & 0x3ff) << 1 |
                     ((word >> 20) & 1) << 11 |
                     ((word >> 12) & 0xff) << 12)
        if immediate & (1 << 20):
            immediate -= 1 << 21
        target = (base + offset + immediate) & 0xffffffff
        if target in targets:
            hits.append(Hit(offset, word, (word >> 7) & 31, immediate, target))
    return tuple(hits), examined


def check_result(hits, examined):
    if examined != SIZE // 2 - 1:
        raise ValueError("incomplete or empty scan")
    if hits != EXPECTED:
        raise ValueError("raw hit set changed (missing, extra, or altered hit)")


def main():
    # Only the pinned image is read. Read one extra byte to reject oversized files.
    with BIN.open("rb") as f:
        data = f.read(SIZE + 1)
    check_pin(data)
    hits, examined = scan(data, BASE, TARGETS)
    print(f"raw JAL-pattern scan: size={len(data)} sha256={SHA256} base=0x{BASE:08x} windows={examined}")
    for h in hits:
        print(f"offset=0x{h.offset:05x} pc=0x{(BASE + h.offset) & 0xffffffff:08x} "
              f"word=0x{h.word:08x} rd=x{h.rd} displacement={h.displacement} target=0x{h.target:08x}")
    check_result(hits, examined)
    print("exact raw hit snapshot verified; matches are not proven callers")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
