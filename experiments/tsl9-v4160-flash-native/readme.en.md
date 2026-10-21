# Readable V4.1.60 Flash C/C++ functions

This new model binds ID2966 SHA-256
`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.
It preserves the old Runtime/BOOT `flash_page.c` separately. The new six functions
were actually compiled as C11/C++17 and strictly linked at their original entry
addresses: quarter64, status8, unlock30, lock14, erase46, program94 bytes. Original
program is100 bytes; that remaining6-byte interval is unowned, not approved padding.

The default verifies only synthetic native-host C/C++ tests, without LLVM or
hardware: `python3 -B experiments/tsl9-v4160-flash-native/verify.py --project-root . --language both`.
`verify.sh` forwards the same arguments. The separate native LLVM CLI and evidence
limits are documented under the case's `implementation/readme.en.md`.

Every synthetic test launch, including six compiled negatives, first verifies a
matching PE/ELF/thin Mach-O machine and width. Architecture comes from the current
Python executable header and runtime pointer width, never the test artifact.
RISC-V ELF243 and unknown/mismatched formats are rejected before subprocess launch;
read-only replay reparses all seven executables. macOS currently requires a thin
Mach-O Python interpreter; universal/fat Python is rejected. Linux/macOS header
fixtures exercise parsing only and are not live OS execution results.

The same readable core uses volatile32 memory access and unbounded busy polls in
RV32 builds. The host provider handles numeric addresses and in-memory fixtures;
unknown conditions/addresses, HALT/TRANSFER and diagnostic poll budgets stop at the
observed external-effect prefix without invented cleanup or a native timeout.
Only normal-return GPR results are claimed. Fresh SP+12 and RA/S0/S1 frame loads
remain explicit obligations. A0 returns the aligned destination, not success; A2
is not a length input. No helper destination-range guard is invented.

The full six-function native component is256 bytes/98 instructions. Save order,
timing, nonreturn GPR prefixes and instruction layouts differ. No BIN is produced,
the previous IRQ image is preserved, and physical Flash/chip/ROM, boot, OTA and
full-image integration remain unproved. Build archives remain local.
