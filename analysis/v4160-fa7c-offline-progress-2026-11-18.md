# v4.1.60: bounded FA7C offline progress

The original image is identified by SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667` (address base `0x8000`). The image is not included here.

## Observation

The routine at `0xfa7c` reads a mode byte at `gp+284`, normalizes bits 1–3 of record byte 4 for modes 1 and 2, and uses bytes at `gp+285` and `gp+286` to determine whether to update bit 0 and branch to `0x12a08`. Comparisons use full byte values. The order of reads and writes matters if record and state addresses overlap; these are synthetic alias examples, not evidence of actual device aliasing.

## Bounded checks

An offline experiment compared a host C projection with a narrow interpreter of the original instruction bytes over 1,088 unique synthetic initial states, including disjoint and selected alias placements. It checked final synthetic memory and the return/tail decision, six fixed examples, and detected five compiled C semantic mutants. A separate static rasm2 control checked 33 instructions (106 bytes) including control targets, with seven tests. Both suites passed normally and under Python optimized mode. The host compiler emitted a missing `vswhere.exe` warning but compiled successfully.

A separate handoff experiment captured a synthetic outer call to `0xfa7c` and replayed the decoder on relocated mapped memory. Three fixed scenarios and one opcode mutation passed in both Python modes. This is not continuous CPU execution: the decoder starts with a fresh register state and the outer routine is not resumed.

## Limits

The experiments use synthetic memory and hooks, do not establish complete access ordering, fault behavior, runtime reachability, installed provider identity, private ABI, or real-device behavior, and stop before executing `0x12a08`. They are not a flashable image or a complete reconstruction. These are progress notes; the underlying local experiment files have not been published in this commit.
