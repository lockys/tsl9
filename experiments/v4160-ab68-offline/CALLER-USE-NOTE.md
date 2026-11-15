# Offline 0xab68 caller-use observations

Target: `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`, SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`, mapped at 0x8000. Observations below come from radare2 6.2.4 standard RISC-V disassembly of the original bytes, not execution. They do not claim a complete caller list.

- `0xab68` loads an unsigned byte from `0x2000bee8` and returns it in `a0`: `auipc a0,0x20001; lbu a0,896(a0); ret`.
- `0x10394` calls that getter. At `0x10398–0x103ac`, `T = (5 * a0 + 10) & 255`. The subsequent comparisons use unsigned values. If `[gp+308]` is zero, `s0 > T` and `T > 59` cause a byte 1 to be written to `[gp+308]` and `0x167a6` to be called with `a0=159`. If the byte is nonzero and `s0 <= T`, it is cleared and `0x167a6` is called with `a0=158`. Otherwise that branch does not write it. These statements assume the call returns normally, the relevant bytes do not change asynchronously, and successful memory accesses; the subsequent call's effects are unknown.
- `0x13ac6` calls the getter. For its returned byte `v`, the instructions `0x13aca–0x13aec` write `([sp+43] & 0x7f) | ((v & 1) << 7)` to `[sp+43]`, then `([sp+44] & 0xf0) | ((v >> 1) & 0x0f)` to `[sp+44]`. Thus bits 5–7 do not influence these two writes. This describes the sequential local fragment, not the eventual packet contents: `0x13af0` immediately calls `0xab72`, after which further instructions modify the same stack region.

The names and real-world meaning of the getter byte, `s0`, and the 158/159 arguments remain unestablished. This is not a CPU execution, full-graph proof, device test, or OTA/flash-readiness claim.
