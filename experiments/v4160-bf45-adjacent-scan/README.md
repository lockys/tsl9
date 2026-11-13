# V4.1.60 adjacent raw-pattern scan

This isolated offline scan reads `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`, requiring exactly 76,800 bytes and SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`. The pin identifies this local input, not its provenance or authenticity. The assumed linear image base is `0x8000`.

At every 2-byte file offset with eight bytes available, the scanner interprets two consecutive little-endian 32-bit words as AUIPC followed immediately by an RV32 byte, halfword, or word load/store (LB/LBU/LH/LHU/LW or SB/SH/SW), requiring the same nonzero AUIPC destination and access base register. It sign-extends both immediates, computes the nominal effective address modulo 2³², and reports patterns whose modular byte range contains `0x2000bf45`. The result includes unaligned accesses; no execution or alignment validity is inferred.

Run from this directory with Python 3, without writing bytecode:

```
python -B scan.py
python -B -m unittest -v
python -B -O -m unittest -v
```

On the pinned input the scan reports three raw patterns: `0xd000` LBU, `0xd00c` SB, and `0xd048` LBU, each at nominal address `0x2000bf45` with width 1. The output includes offsets, raw bytes, base register, signed displacement, and access width.

These are **static raw byte patterns**, not evidence of execution or actual instruction boundaries. Data and overlapping decodings may produce false positives; the assumed base may be wrong. The scan excludes compressed instructions, non-adjacent sequences, other address constructions, and other access forms. It does not establish reachability, ownership, a complete list of writers or readers, or runtime behavior. No target is executed, emulated, or flashed.
