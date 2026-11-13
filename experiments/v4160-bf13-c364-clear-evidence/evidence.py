#!/usr/bin/env python3
"""Pinned, bounded RV32I/C static decoder. No firmware execution."""
from hashlib import sha256
from pathlib import Path
import sys

BASE, SIZE = 0x8000, 76800
PIN = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BIN = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
START, END = 0xc364, 0xc3d4
# Independently transcribed instruction expectations, including registers and signed immediates.
# Register numbers follow RISC-V ABI: x0=zero, x1=ra, x2=sp, x8=s0.
ROWS = (
(0xc364,'addi',2,2,-16), (0xc366,'sw',8,2,8), (0xc368,'sw',1,2,12),
(0xc36a,'auipc',15,0x20000000), (0xc36e,'lbu',15,15,-1114),
(0xc372,'auipc',8,0x20000000), (0xc376,'addi',8,8,-1142),
(0xc37a,'beq',15,0,0xc382), (0xc37c,'addi',10,0,0), (0xc37e,'jal',1,0xef76),
(0xc382,'lbu',15,8,22), (0xc386,'andi',15,15,255),
(0xc38a,'beq',15,0,0xc392), (0xc38c,'addi',10,0,0), (0xc38e,'jal',1,0xbd6e),
(0xc392,'lbu',15,8,23), (0xc396,'andi',15,15,255),
(0xc39a,'beq',15,0,0xc3a4), (0xc39c,'auipc',15,0x20000000),
(0xc3a0,'sb',0,15,-1161), (0xc3a4,'lw',1,2,12), (0xc3a6,'lw',8,2,8),
(0xc3a8,'addi',2,2,16), (0xc3aa,'jalr',0,1,0),
(0xc3ac,'addi',15,0,50), (0xc3b0,'auipc',14,0x20000000),
(0xc3b4,'sb',15,14,-1186), (0xc3b8,'addi',10,0,1), (0xc3ba,'jal',0,0x9454),
(0xc3be,'lui',15,0x40000), (0xc3c2,'lw',6,15,72),
(0xc3c6,'addi',12,0,28), (0xc3c8,'addi',11,0,0),
(0xc3ca,'auipc',10,0x20000000), (0xc3ce,'addi',10,10,-1230),
(0xc3d2,'jalr',0,6,0),
)
WINDOW = bytes.fromhex('411122c406c69707002083c767ba170400201304a4b881c70145ef20903f8347640193f7f70f81c70145eff01f9e8347740193f7f70f89c797070020a38b07b6b2402244410182809307200317070020230ff7b405456fd0af89b707040003a387047146814517050020130525b30283')


def need(condition, message):
    if not condition:
        raise ValueError(message)


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def decode(data, pc):
    need(len(data) >= 2, f'truncated instruction at {pc:#x}')
    h = int.from_bytes(data[:2], 'little')
    if h & 3 != 3:
        op, f = h & 3, h >> 13
        rd, rs2 = (h >> 7) & 31, (h >> 2) & 31
        imm = signed(((h >> 12) & 1) << 5 | ((h >> 2) & 31), 6)
        if op == 1 and f in (0, 2):
            need(rd != 0, 'reserved compressed immediate')
            return 2, ('addi', rd, rd if f == 0 else 0, imm)
        if op == 2 and f == 6:
            offset = ((h >> 9) & 15) << 2 | ((h >> 7) & 3) << 6
            return 2, ('sw', rs2, 2, offset)
        if op == 2 and f == 2:
            need(rd != 0, 'reserved c.lwsp')
            offset = ((h >> 4) & 7) << 2 | ((h >> 12) & 1) << 5 | ((h >> 2) & 3) << 6
            return 2, ('lw', rd, 2, offset)
        if op == 1 and f == 6:
            off = (((h >> 12) & 1) << 8 | ((h >> 10) & 3) << 3 |
                   ((h >> 5) & 3) << 6 | ((h >> 3) & 3) << 1 | ((h >> 2) & 1) << 5)
            return 2, ('beq', 8 + ((h >> 7) & 7), 0, pc + signed(off, 9))
        if op == 2 and f == 4 and ((h >> 12) & 1) == 0 and rs2 == 0 and rd:
            return 2, ('jalr', 0, rd, 0)
        raise ValueError(f'unsupported compressed encoding {h:04x} at {pc:#x}')
    need(len(data) >= 4 and (h & 0x1f) != 0x1f, f'truncated or unsupported length at {pc:#x}')
    w = int.from_bytes(data[:4], 'little')
    opcode, rd, f, rs1, rs2 = w & 127, (w >> 7) & 31, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31
    imm = signed(w >> 20, 12)
    if opcode == 0x17:
        return 4, ('auipc', rd, w & 0xfffff000)
    if opcode == 0x37:
        return 4, ('lui', rd, w & 0xfffff000)
    if opcode == 0x13 and f in (0, 7):
        return 4, ('addi' if f == 0 else 'andi', rd, rs1, imm)
    if opcode == 0x03 and f in (2, 4):
        return 4, ('lw' if f == 2 else 'lbu', rd, rs1, imm)
    if opcode == 0x23 and f == 0:
        return 4, ('sb', rs2, rs1, signed(((w >> 25) << 5) | ((w >> 7) & 31), 12))
    if opcode == 0x6f:
        off = ((w >> 31) << 20 | ((w >> 12) & 255) << 12 |
               ((w >> 20) & 1) << 11 | ((w >> 21) & 1023) << 1)
        return 4, ('jal', rd, pc + signed(off, 21))
    raise ValueError(f'unsupported instruction {w:08x} at {pc:#x}')


def check_pin(data):
    need(len(data) == SIZE and sha256(data).hexdigest() == PIN, 'BIN size/SHA-256 mismatch')


def inspect(window, rows=ROWS):
    need(len(window) == END - START, 'window length mismatch')
    need(window == WINDOW, 'window bytes mismatch')
    need(bool(rows), 'empty instruction fixture')
    pc, offset, actual = START, 0, []
    while offset < len(window):
        size, fields = decode(window[offset:], pc)
        need(offset + size <= len(window), 'partial final instruction')
        actual.append((pc,) + fields)
        offset += size
        pc += size
    need(pc == END and tuple(actual) == tuple(rows), 'instruction fixture mismatch')
    return actual


def pcrel(pc, immediate):
    return (pc + 0x20000000 + immediate) & 0xffffffff


def run():
    data = BIN.read_bytes()
    check_pin(data)
    rows = inspect(data[START-BASE:END-BASE])
    need((pcrel(0xc36a,-1114), pcrel(0xc372,-1142), pcrel(0xc39c,-1161),
          pcrel(0xc3b0,-1186), pcrel(0xc3ca,-1230)) ==
         (0x2000bf10,0x2000befc,0x2000bf13,0x2000bf0e,0x2000befc), 'PC-relative targets changed')
    print(f'PIN {PIN}, {SIZE} bytes; VA=0x8000+file offset')
    for row in rows:
        print(f'{row[0]:08x} {row[1:]}')
    print(f'{len(rows)} complete instructions [0x{START:x},0x{END:x}); targets verified')


if __name__ == '__main__':
    try:
        run()
    except (OSError, ValueError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        sys.exit(1)
