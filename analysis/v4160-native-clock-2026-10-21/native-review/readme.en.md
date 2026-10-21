# Readable native clock components

The new `native_clock.c` has been compiled as actual freestanding RV32 C11 and C++17, then linked into `COMPONENT-ONLY-NOT-FIRMWARE.elf`. Both modes emit the same function bytes: clock query is **170 bytes / 59 instructions**, versus the captured original 174 bytes / 58 instructions; clock fields is **44 bytes / 14 instructions**, versus the original 40 bytes / 11 instructions. The field function exceeds its original extent by four bytes with this compiler profile. Neither function has been placed at an original firmware address.

The native objects and linked components have no undefined symbols, runtime libcalls, writable data, or original-address aliases. They contain exactly the two newly named reconstruction functions. ELF class, machine, RVC/soft-float ABI flags, and RV32IMAC integer ISA attributes are checked. Linking at diagnostic address `0x1000` preserves both functions' machine bytes.

Each function's entire ELF byte extent is matched against raw disassembly bytes with contiguous addresses and complete instruction framing. Unknown instruction forms, unparsed interior/trailing lines, interior labels, gaps, and truncation are rejected. Every direct branch targets a real instruction boundary inside the same function, and all fallthroughs remain inside it. The compiled functions perform exactly four and three explicit GP-read primitives, respectively, and never write GP. Load/store width allowlists reject unsupported accesses; CSR operations, traps, external calls, and hidden helper functions are rejected.

The LLVM IR additionally checks all live GP reads and memory clobbers, the separate GP-relative addresses `+108`, `+64+index`, `+382`, and `+380`, six static RCC read sites, one EXTEN read site, the unsigned table-byte read, two 32-bit output stores, masked unsigned shifts, unsigned division by 8,000,000, and byte truncation before multiplication by 1,000. Static access-site counts include alternative branches; they are not a claim that every execution follows one fixed effect list.

Each language actually compiles and rejects five source mutants: fixed GP, wrong global offset, wrong table width, lost quotient truncation, and signed division. Twelve transcript controls per language cover missing first/interior/final rows, changed raw instruction bytes, and unparsed interior/trailing lines for both functions. `results.json` records the real receipts, source/tool identities, and the separate parent hosted semantic tests.

## Fresh compilation from a published checkout

Python 3.10+ and local LLVM tools supporting RV32IMAC are required:

```sh
python3 analysis/v4160-native-clock-2026-10-21/native-review/verify_native.py \
  --project-root . \
  --clang /path/to/clang \
  --linker /path/to/ld.lld \
  --objdump /path/to/llvm-objdump \
  --language both
```

Alternatively use `--tool-dir /path/to/llvm/bin`. The investigation workspace uses `apk-analysis/tsl9-v4160-native-clock-2026-10-21/` instead of the published `analysis/v4160-native-clock-2026-10-21/` prefix. The fresh CLI needs only the new C/header, its shipped Python scripts, and local LLVM; old ignored native image archives are unnecessary. The verified toolchain is Android NDK 27.1.12297006, Clang 18.0.2, with `--target=riscv32-unknown-elf -march=rv32imac -mabi=ilp32 -Os -ffreestanding -mno-relax`. Complete flags and executable hashes are recorded in every receipt. Other compiler forms outside the implemented static proof profile fail explicitly.

For a read-only replay of retained original local archives, run `check_native.py --project-root . --require-local-builds`. Without the final flag, missing archives are listed explicitly; a sealed-metadata check does not claim a fresh compile. Generated object/ELF/IR/log archives remain local and are excluded from source publication.

## Evidence limits and integration work

These are **native structural and primitive proofs**, with selected unsigned IR properties. The clock query has branches. The machine verifier does not execute those branches, emulate registers/memory, or establish full native branch-path semantic equivalence. Parent hosted tests validate the shared C calculations through explicit synthetic I/O; they are separate evidence, not RV32 execution or physical hardware validation.

The ordinary C interfaces change the original A0/A1 and other caller-saved register residues. Preserving GP is not a complete original C/IRQ ABI proof. The exact original call-chain obligations, asynchronous interrupt behavior, remaining four-byte field overrun, fixed address layout, unknown ROM/resident implementation, actual board/MCU, peripheral effects, and Bluetooth OTA compatibility still need proof. The old native image gate is untouched. No firmware BIN is produced, no original/rebuilt RV32 code is executed, and no device I/O or network access occurs. This component is not ready for flashing.
