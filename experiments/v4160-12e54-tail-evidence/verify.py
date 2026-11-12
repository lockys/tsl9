#!/usr/bin/env python3
"""Static checks only; addresses are RV32 virtual addresses, image based at 0x8000."""
import hashlib
import sys
from pathlib import Path

BASE = 0x8000
SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
WINDOWS = {
    0x12e54: bytes.fromhex('b7070400fc476d71232611100a85130600109795ff1f9385e5628297378507088a8513050590ef601fd98320c11051618280'),
    0x12e86: bytes.fromhex('b70704004111bc4722c41794ff1f1304446006c6228513060010814582979307a005a30ff40eb717430b938727401cc0b717450d938747c45cc0b7370c2b9387a7c01cc4b7571f5ff9075cc4b727212a938707e21cc82244b24041016ff03ff7'),
}

class EvidenceError(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise EvidenceError(message)

def sign(value, bits):
    return (value ^ (1 << (bits - 1))) - (1 << (bits - 1))

def address(base, offset):
    require(0 <= base <= 0xffffffff and -(1 << 31) <= offset < (1 << 31), 'address operands out of RV32 range')
    return (base + offset) & 0xffffffff

def word(data, pc):
    off = pc - BASE
    require(off >= 0 and off + 4 <= len(data), 'instruction outside image')
    return int.from_bytes(data[off:off+4], 'little')

def pair(data, pc, relative=False, addi_pc=None, rd=None):
    u, i = word(data, pc), word(data, pc + 4 if addi_pc is None else addi_pc)
    require(rd is None or (u >> 7) & 31 == rd, 'invalid upper destination')
    require(u & 0x7f == (0x17 if relative else 0x37), 'expected upper instruction')
    require(i & 0x707f == 0x13 and (i >> 15) & 31 == (u >> 7) & 31 and (i >> 7) & 31 == (u >> 7) & 31, 'invalid addi pair')
    return address(address(pc if relative else 0, sign(u & 0xfffff000, 32)), sign(i >> 20, 12))

def call_argument(data):
    # The intervening 16-bit instruction is c.mv a1,sp, not part of the pair.
    off = 0x12e74 - BASE
    require(off >= 0 and data[off:off + 2] == bytes.fromhex('8a85'), 'invalid intervening instruction')
    return pair(data, 0x12e70, addi_pc=0x12e76, rd=10)

def jal_target(data, pc, rd):
    w = word(data, pc)
    require(w & 0x7f == 0x6f and (w >> 7) & 31 == rd, 'invalid jal')
    imm = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
    return address(pc, sign(imm, 21))

def verify_windows(data):
    for pc, expected in WINDOWS.items():
        off = pc - BASE
        require(data[off:off + len(expected)] == expected, f'window mismatch at {pc:#x}')

def verify(data):
    require(len(data) == 76800, 'image length mismatch')
    require(hashlib.sha256(data).hexdigest() == SHA256, 'image hash mismatch')
    verify_windows(data)
    require(pair(data, 0x12e66, True) == 0x2000c494, 'source address mismatch')
    require(pair(data, 0x12e90, True) == 0x2000c494, 'destination address mismatch')
    require(pair(data, 0x12eac) == 0x0b431402, 'constant 0')
    require(pair(data, 0x12eb6) == 0x0d450c44, 'constant 1')
    require(pair(data, 0x12ec0) == 0x2b0c2c0a, 'constant 2')
    require(pair(data, 0x12ed2) == 0x2a211e20, 'constant 4')
    # The fourth immediate is compressed c.addi rather than a 32-bit addi.
    w = word(data, 0x12eca)
    h = int.from_bytes(data[0x12ece-BASE:0x12ed0-BASE], 'little')
    require(w & 0x7f == 0x37 and (w >> 7) & 31 == 15 and h & 0xef83 == 0x0781, 'invalid compressed constant')
    imm = sign(((h >> 12) & 1) << 5 | ((h >> 2) & 31), 6)
    require(address(sign(w & 0xfffff000, 32) & 0xffffffff, imm) == 0x5f1f501e, 'constant 3')
    require(jal_target(data, 0x12ee2, 0) == 0x12e54, 'tail target')
    require(jal_target(data, 0x12e7a, 1) == 0x9c0a, 'call target')
    require(call_argument(data) == 0x08077900, 'call argument')
    return True

def main():
    try:
        verify(Path(sys.argv[1]).read_bytes() if len(sys.argv) > 1 else IMAGE.read_bytes())
    except (OSError, EvidenceError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1
    print('OK: pinned image, windows and RV32 arithmetic')
    return 0

if __name__ == '__main__':
    sys.exit(main())
