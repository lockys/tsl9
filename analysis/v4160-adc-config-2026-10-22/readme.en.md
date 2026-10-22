# ADC configuration in C/C++ and original callback dependencies

[繁體中文](README.md)

One readable C algorithm reconstructs original `0x1892E..0x18986`, genuinely compiled as C11/C++17 and tested with synthetic typed IO. A native adapter uses real volatile IO but is only compiled and statically inspected. **No newly rebuilt firmware BIN, existing-component replacement or verified flashability.**

An88-byte original source-evidence slice is retained for verification; it is not rebuilt firmware or an opcode input to compilation. The original88-byte/37-instruction function has14 ordered accesses. Three fresh read/modify/write32 groups consume complete32-bit configuration fields and one byte. Masks are `0xE0F0FEFF`, `0xFFF1F7FD`, `0xFF0FFFFF`; the final field is `((byte-1)&255)<<20`. The reconstruction retains access order, uint32 wrap, alias feedback and high bits without narrowing configuration values.

| Measurement | Result | Boundary |
| --- | --- | --- |
| Producer HOST C/C++ | 80cases,6864checks,3actual semantic controls each | Synthetic typed IO, not original firmware execution |
| Independent HOST C/C++ | 74cases,2904checks,3actual semantic controls each | Alias, dynamic reads and14-step stop prefixes |
| Selected native entry | 102bytes/38instructions, no call/frame | 14bytes larger than original |
| Complete native object | 5genuine global FUNC,254bytes/93instructions, UND0/RELA0 | Includes4unselected functions; no linked image |

Normal A0/A1 are preserved, but native code additionally writes A2/A6/A7 versus original A3/A4/A5. This particular caller overwrites A2/A6 later, narrowing only part of its normal-path difference. Original callback A7 is preserved, so the new A7 write can escape. Full register/fault/asynchronous-prefix and extent contracts remain unproved. [Implementation](implementation/readme.en.md); [independent tests and native differences](model-review/readme.en.md).

Eight new source ranges cover386bytes/148rows; the364-byte callback and prior106-byte dependency were reread. All13 direct call sites have closed restricted dependencies. Under a valid private144-byte stack disjoint from code/MMIO/configuration, normal accesses, no adverse asynchronous changes, and a finite read observing status bit1, normal return preserves SP/RA/S/GP/TP. Termination is not guaranteed: the original polling loop has no timeout. Channel configuration writes A6, so whole-GPR preservation is false.

The callback selects channel16, sequence1, sample7; its normal result is the low16bits of fresh READ32(`0x4001244C`), not established Celsius. Reset bit9 at `0x4002100C` is cleared without a whole-word snapshot. Config word52 preservation requires disjointness from the explicit stack/MMIO write sets; entire initialization lifetime and installed identity remain unknown. [Source contract and controls](source-review/readme.en.md).

Previously captured official CH32V20x ADC1/ADC2 addresses and CTLR1/CTLR2/RSQR1 field order corroborate a family candidate, not the physical chip/package. [Header excerpts, full-source hash and provenance](hardware-reference.json); [official RISC-V field excerpts](instruction-reference/readme.en.md). No opcode generation or CPU/ISA execution occurred.

Feature proposal: an offline ADC report displaying raw16 values, channel/sample configuration and incomplete calibration/poll diagnostics. Physical temperature display needs actual hardware/calibration evidence. This is not an implemented hardware feature or a change to original polling behavior.

Default checks validate metadata; actual firmware/ELF/object reads require explicit paths. No native adapter, RV32, MMIO or hardware execution. The existing550-byte component and77,824-byte NOT-FLASH-VALIDATED image remain unchanged. Python entry points were tested; the previous Git Bash `NtCreateDirectoryObject0xC0000022` blocker was not retried or bypassed, so shell runtime remains unverified.
