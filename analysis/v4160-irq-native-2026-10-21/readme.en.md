# Native IRQ reconstruction evidence

[繁體中文](README.md)

This round corrects compiler allocation and the readable C/C++ core; the full objective remains an original-hardware-compatible BIN. The new core is `experiments/tsl9-v4160-irq-native/`. Previous models and failure evidence remain unchanged.

| Question | Evidence | Still unproved |
| --- | --- | --- |
| Why the old core required SP | compiler-diagnosis actual spill/outliner artifacts | Complete allocator internals |
| New hosted behavior | Canonical and independent C11/C++17 suites with compiled mutations | Host tests do not prove native bridges |
| Helper original placement | compiler-review exact four original-address 30-byte matches | Full-image integration |
| Normal registers and effects | Independent abi-review bytes plus complete machine/20-effect/IR checks | Intermediate/asynchronous IRQ equivalence |
| Main extent fit | 180 bytes exceeds original 144; rejected | Alternative placement and all references |
| Additional C++ allocations | `.eh_frame` 120 object /124 linked bytes; all-allocated ownership false | Metadata storage/integration |

source-design, compiler-diagnosis, source-review, abi-review and compiler-review are sealed independently. Delivery contains sources, checkers and selected receipt metadata, excluding historical build archives. Replaying the early abi-review requires its original workstation candidate builds. Published copies compare fresh per-function bytes with that sealed result; missing archives are not reported as a fresh replay of the earlier audit.

```sh
sh experiments/tsl9-v4160-irq-native/verify.sh --language both
sh experiments/tsl9-v4160-irq-native/verify-native.sh --tool-dir /path/to/llvm/bin --language both
```

Python can directly launch the corresponding checkers. The native CLI accepts explicit `--project-root`, `--tool-dir` and `--firmware`. The original is V4.1.60 ID2966 SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`. Original bytes are read only. There is no RV32 execution/emulation, vendor request, BLE/UART/CAN/physical Flash I/O or new BIN.
