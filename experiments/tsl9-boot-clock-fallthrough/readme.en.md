# Clock fall-through component

[繁體中文](README.md)

The readable C core preserves all 85 computational IR lines and 216 computational native bytes. The architectural entry falls directly into the adjacent C body; its final SP+16 / RET port returns through the original RA. Actual C11/C++17 builds are **232 bytes / 93 instructions**, eight bytes smaller than the previous component.

- Nominal linked entry `0x1874A`, body `0x18756`, end `0x18832`: no overlap with the next function at `0x18834`.
- Two real FUNC definitions; no aliases, UND, ABS, relocations, extra frame, spills or RA writes.
- Eighteen negative controls per language and complete ELF/IR/tool/header/command/MD/source/artifact checks pass. These are offline static results.
- The original `0x18832..0x18834` cold jump is not free space. The bounded direct-branch scan does not cover indirect/resident/BOOT/IRQ entries.
- Reset/caller composition remains unverified. Curated `src/native/clock/clock_init.c` retains the previous integrated version. No BIN is generated; `--require-firmware-ready` rejects the candidate.

Set `TSL9_LLVM_BIN` to the reviewed local tool directory, then run from the project root using a new build directory:

```sh
python -B experiments/tsl9-boot-clock-fallthrough/verify.py --project-root . --tool-dir "$TSL9_LLVM_BIN" --build-root experiments/tsl9-boot-clock-fallthrough/build/local-v1
python -B experiments/tsl9-boot-clock-fallthrough/verify.py --project-root . --tool-dir "$TSL9_LLVM_BIN" --replay experiments/tsl9-boot-clock-fallthrough/build/local-v1/c/verification.json
```

Tool/header hashes currently bind the reviewed Windows LLVM profile. Other compilers/platforms require separate evidence. Public receipts omit local build artifacts; replay requires matching retained artifacts. Build first in a new checkout.

[Source and verification summary](../../analysis/clock-fallthrough-2026-10-23/summary.json) · [C receipt](../../analysis/clock-fallthrough-2026-10-23/receipts/c.json) · [C++ receipt](../../analysis/clock-fallthrough-2026-10-23/receipts/cpp.json) · [OTA evidence opportunity](../../analysis/clock-fallthrough-2026-10-23/ota-evidence-opportunity.en.md)
