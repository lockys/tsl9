# Native memory IO and three-argument C/C++ entries

[繁體中文](README.md)

The previously sealed readable C algorithms now have real volatile byte/word IO and FENCE.I ports, with three uint32 arguments and one uint32 result at each native C11/C++17 public entry. **This is compilation and static inspection only: no direct IO, RV32/hardware execution, link or new BIN.**

[Native source](../../experiments/tsl9-resident-memory-native/README.md) | [Compilation](implementation/README.md) | [Independent ABI review](abi-review/README.md) | [Original App callback](callback-review/README.md)

The first ordinary same-TU profile produced30-byte wrappers with64-byte frames, internal context/structure-return calls, and changed A1/A2. The complete object was320B/125 instructions/three genuine CALL_PLT relocations/UND0.

One motivated source adjustment inlines the shared algorithms and IO/helpers and adds a narrow real A0/A1/A2 register boundary. Current public compare/fill/copy entries are52/48/52 bytes, totaling **152B/52 instructions**. They contain no context/sret, call or explicit SP/RA/GP/S/A1/A2 write. Normal A0 results match the conditional reference algorithms:0/1, advanced destination, and original destination respectively.

Eight genuine global functions not called by these entries remain allocated (230B/86 instructions). The whole object is382B/138 instructions, UND0/RELA0. It is not a linked image, and its whole-object size is not the selected entry size.

**Full original ABI remains unproved and has measured differences.** Compare additionally writes A6, fill A3/A6/A7, copy T0/A7. Scratch liveout values differ. Compare/fill update A0 at different points around potentially faulting byte accesses. Fill48B exceeds its original46B; shorter compare/copy code does not establish ownership of original tails. No in-place, transient/IRQ/fault or physical equivalence is admitted. Original copy itself uses A6, so each reference gets its own register contract.

The original App field44 target197F0 has a source-CFG range364B/130 instructions ending1995C (exclusive), with13 call sites/12 unique targets and one polling loop without an encoded timeout. ELF supplies only a NOTYPE size0 entry, not an original FUNC364. The aligned32-byte private-stack path of8520 and two small RCC leaves19124/1908C narrow early effects. The next unresolved dependency is1987A→188E2. The tsCB/temperature name remains a header inference; callback-wide preservation or config52-zero lifetime is not proved.

The fixed Windows LLVM recipe adds zifencei for the actual FENCE.I; there is no flag sweep. Metadata defaults are separate from explicit object/FW/ELF reads. Callback ELF checks cover only its slice within the existing548-byte owner, not whole-image provenance. Historical ordinary artifacts are archived honestly after the source change, without pretending the current root replays old source.

The shared algorithms are unchanged. Old HOST matrices are not rerun, and this direct-MMIO port is never executed on HOST. There is no fake numeric provider, copied-opcode generation, missing-code padding or third profile. Python/POSIX shell entries are portable; only the fixed Windows native toolchain is measured.

Full register/prefix/IRQ ABI, placement/Flash-NV ownership, installed ROM/BOOT/board identity and BLE OTA acceptance/recovery remain open. The550-byte OTA experiment and existing BIN are unchanged. Offline configuration diagnostics remain a proposed addition, not an installed feature.
