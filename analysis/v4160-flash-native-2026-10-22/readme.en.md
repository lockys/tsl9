# Readable C/C++ reconstruction of V4.1.60 Flash functions

[繁體中文](README.md)

Six functions from vendor ID2966 V4.1.60 now share C11/C++17 source for synthetic host tests and original-address RV32 component builds. The original source evidence covers 262 bytes / 99 instructions. Neither original nor rebuilt RV32 is executed or emulated. No hardware or vendor API is accessed.

| Entry | Function | Original bytes | C/C++ component bytes |
| --- | --- | ---: | ---: |
| `0x9C0A` | Quarter-page sequence | 64 | 64 |
| `0x18E90` | Status write | 8 | 8 |
| `0x18E98` | Ordered unlock keys | 30 | 30 |
| `0x18EB6` | CTLR lock | 14 | 14 |
| `0x18EC4` | 256-byte aligned erase sequence | 46 | 46 |
| `0x18EF2` | 64 fresh word reads/writes | 100 | 94 |

The native total is 256 bytes. Status and lock have 22 original-identical bytes. Other functions are checked for ordered MMIO, polling and normal-return/frame contracts; not all bytes or pointwise states are identical. The algorithm is C with narrow compiler-assembly interfaces for CSR, fixed registers and explicit JALs.

The quarter wrapper has a 32-byte frame and reloads the live source from `SP+12` after erase. It calls unlock, status 49, erase, program and lock, clearing then unconditionally setting CSR `0x800` mask 136. This is not restoration of the original CSR value. Normal A0 is the aligned destination, not a hardware success code. Program's normal A2 is 256, A6 is the final fresh source word, and A1 is preserved.

Each host language passes 5 groups / 481 cases / 247,191 assertions and rejects six actually compiled/executed semantic mutations. The independent expected-effect oracle adds 12 scenarios / 8,964 assertions and twelve compiled mutation rejections per language. These use synthetic providers. Native static review checks six functions, five JALs and LLVM IR, with fifteen machine-byte and three IR negative controls per language.

Native polls remain unbounded; host observation budgets do not introduce native timeouts. Unknown or nonreturning provider paths must not manufacture cleanup or success. Frame save order and program A0-alignment timing differ from original instructions. Nonreturn/fault GPR prefixes, pointwise and asynchronous equivalence remain unproved.

The six-byte gap at `0x18F50..0x18F55` has no new proved storage owner. There is no padding, adjacent-section borrowing or new BIN. The previous 76,800-byte IRQ offline image remains unchanged and **NOT-FLASH-VALIDATED**. Chip, installed ROM/BOOT, physical Flash and BLE OTA compatibility remain unproved.

From the repository root:

```sh
python experiments/tsl9-v4160-flash-native/verify.py --language both
python analysis/v4160-flash-native-2026-10-22/implementation/verify_native.py --project-root . --tool-dir /absolute/path/to/LLVM/bin --language both
python analysis/v4160-flash-native-2026-10-22/callers/inspect_callers.py --project-root . --check
```

Host verification requires Python and a C11/C++17 compiler. Native checks additionally require the pinned Clang, LLD and LLVM objdump tools and never execute the component. POSIX wrappers are provided; Windows results do not establish shell/Linux/macOS/CI execution. Fresh destination compilation, seal/member checking and historical-build replay are separate evidence levels. Re-reading original carrier or frontier artifacts requires their matching build inputs.

Before each synthetic test launch, the host entry checks the output format and local machine architecture, rejecting RISC-V ELF and incompatible executables. This runner-only change leaves all six function sources unchanged. The original `review` remains an immutable pre-guard archive; [review-v2](review-v2/readme.en.md) binds the current runner and new host receipts and is the current independent review entry.

Architecture comes from the running Python executable's header. macOS currently requires thin Mach-O Python; universal/fat Python is rejected before launch. Linux/macOS header fixtures test parsing branches only and do not establish live platform results.

See [source/ABI](source/README.md), [bounded callers](callers/README.md), [native review](compiler-review/readme.en.md), and [integration frontier](integration-frontier/readme.en.md). Existing [feature proposals](../v4160-irq-callframe-2026-10-21/feature-candidates/readme.en.md) remain distinct from implemented functions; no new vehicle-control feature is added.

Next, account for all six original storage extents, incoming aliases and eleven owned relocation records before complete-image export verification. Offline integration cannot replace original-hardware startup, ROM, memory, interrupt and updater compatibility evidence.
