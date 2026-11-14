#!/usr/bin/env python3
"""Bounded call-boundary projection; stops before unknown downstream effects."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
WINDOWS = {
    0x102e6:'efa0bfdc83c751138de78547a38af112efc0dfd59147631ef5001305500901a8',
    0x10310:'1305a008ef602049',
    0x10318:'1307b00893866113294695452285ef703ff2',
    0xd052:'17f5ff1f034525ef8280',
    0x167a6:'011122cc26ca4ac84ec606ce52c456c2aa840144938901061309e00f83a70900a29703c707006316970003c51700efe0dfdf0904e31424ff',
}


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def jal_target(raw, pc, dest):
    w = int.from_bytes(raw, 'little')
    need(w & 0x7f == 0x6f and (w >> 7) & 31 == dest, 'unexpected JAL encoding')
    imm = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
    if imm & (1 << 20):
        imm -= 1 << 21
    return (pc + imm) & 0xffffffff


def verify_windows(image):
    for pc, text in WINDOWS.items():
        expected = bytes.fromhex(text)
        need(image[pc-0x8000:pc-0x8000+len(expected)] == expected, f'instruction mismatch at {pc:#x}')
    def at(pc):
        return image[pc-0x8000:pc-0x8000+4]
    for pc, target in [(0x102e6,0xb0b0),(0x102f6,0xd052),(0x10314,0x167a6),(0x10326,0x8248),(0x167d4,0x155d0)]:
        need(jal_target(at(pc),pc,1)==target, f'call target mismatch at {pc:#x}')


def route(flag, observed_byte, initial_a1):
    # Successful accesses, no interruptions or intervening state changes.
    # On the zero path 0xd052 reads a byte and leaves a1 unchanged.
    if flag:
        return 0x8248, 5
    if observed_byte != 4:
        return 0x8248, 5
    return 0x167a6, initial_a1


def main():
    image = BIN.read_bytes()
    need(len(image)==76800 and hashlib.sha256(image).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667', 'BIN identity mismatch')
    verify_windows(image)
    for flag in range(256):
        for byte in range(256):
            original, candidate = route(flag,byte,1), route(flag,byte,0x2000c000)
            if flag == 0 and byte == 4:
                need(original == (0x167a6,1) and candidate == (0x167a6,0x2000c000), 'changed a1 boundary')
            else:
                need(original == candidate == (0x8248,5), 'a1 overwritten boundary')
    print('PASS: 65536 projected flag/byte pairs; 0,4 reaches 0x167a6 with differing a1; all others reach 0x8248 after a1=5')
    # Exercise each byte mutation directly against the window check, rather than
    # relying only on the full-image hash.
    tested = 0
    for pc, text in WINDOWS.items():
        for i in range(len(bytes.fromhex(text))):
            changed = bytearray(image)
            changed[pc-0x8000+i] ^= 1
            try:
                verify_windows(changed)
            except ValueError:
                tested += 1
            else:
                raise ValueError('mutated witness accepted')
    print(f'PASS: rejected {tested} independent window-byte mutations')
    print('LIMIT: segmented conditional projection; 0x167a6 downstream calls, tail-return destinations and hardware not established')


if __name__ == '__main__':
    main()
