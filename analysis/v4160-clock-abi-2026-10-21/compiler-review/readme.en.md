# Clock register preservation and compiler feasibility

Actual Clang 18 builds establish a narrower register-allocation candidate for the new C/C++ clock functions. The finalized query is **196 bytes / 64 instructions**, compared with the original 174 bytes. The finalized fields function is **38 bytes / 10 instructions**, compared with the original 40 bytes. The query still exceeds its original extent by 22 bytes; this milestone does not establish a drop-in image.

Each unit is compiled separately. All integer registers other than query allocator registers X13–X15, or fields allocator registers X14–X15, are reserved with `-ffixed-xN`. Query X12 is assigned only through the explicit external-mask primitive. Actual raw instruction destination fields are checked against both the disassembly destination and the original write allowlist. Both functions preserve A0/A1 and have no SP/GP/RA writes, stack accesses, hidden calls, undefined symbols, writable data, or original-symbol aliases in the emitted component.

The field function uses a real unsigned `DIVU`, preserves byte and halfword stores at GP+382 and GP+380, and matches a complete straight-line instruction pattern establishing normal final A4=1000 and A5=(fresh GP+108 word DIVU 8000000 & 255)*1000. The byte store uses the unmasked quotient register; its low eight bits equal the masked quotient byte. Intermediate register assignments differ from the original, so this is not pointwise register or asynchronous IRQ equivalence.

The query retains its C-level path-dependent A3 formula and conditional external-PLL A2 assignment. The compiler proof covers all 196 actual ELF bytes, independently checks every encoded destination, and verifies its complete internal acyclic CFG, including the interior RET and trailing fallback blocks. It does not execute branch conditions or prove complete machine-level query semantics. The separate hosted tests cover the shared C calculation, memory effects, and register commitments. Preserving a write subset alone would be insufficient: source A3 survives later calls and reaches an opaque downstream callback.

Both C11 and C++17 compile and link `COMPONENT-ONLY-NOT-FIRMWARE.elf`. Each mode actually compiles, links, and rejects three controls: an A0 write, an SP write, and an incorrect final A4. Fourteen transcript controls per mode reject omitted/truncated instruction rows, raw byte changes, display-only destination changes, and unparsed lines. The verifier compares all raw bytes and destination fields, checks RV32IMAC/RVC/soft-float attributes, and rejects escaping branches, CFG cycles, hidden runtime helpers, or unsupported instruction forms.

## Bounded investigations and rejected alternatives

Ordinary clock C clobbered A0/A1. Reserving only A0/A1 still allowed an extra A6 write. Reserving the full original query clobber subset could produce 174 bytes for the older memory-only C, but did not preserve its required A3 residue. The old fields body needed a third temporary and failed when SP and all registers except A4/A5 were reserved. Ordinary constant division emitted a magic multiplication; `-Oz` or an explicit DIVU primitive reduced it, but a copied GP value still left 42 bytes.

An empty volatile asm output bound to physical GP removed unnecessary GP copies without emitting a GP assignment. Native disassembly, rather than that source declaration alone, establishes GP preservation. Correct fields final registers additionally required an empty read/write A4 barrier before the multiplication; pure input-only final commitments produced 42 or 46 bytes. The adopted opaque A2 external mask avoided the query allocator failure. An A3 comparison-constant reuse experiment still required SP and was rejected. No allocation search continued after these bounded experiments.

One early GP probe script accidentally reused its disassembly string as the next optimization variant's C source. Its resulting invalid-source failures are retained locally but excluded from compiler-support conclusions; the corrected six-profile report supersedes it. Early missing-native-macro failures were corrected in the new product header, then the final four C/header files were frozen and independently rebuilt. `results.json` identifies final receipts and the useful archived probe reports.

## Fresh native build

Python 3.10+ and local LLVM tools supporting RV32IMAC are required. From a published checkout:

```sh
python3 analysis/v4160-clock-abi-2026-10-21/compiler-review/verify_compiler.py \
  --project-root . --tool-dir /path/to/llvm/bin --language both
```

Alternatively supply `--clang`, `--linker`, and `--objdump` executable paths. The investigation workspace prefix is `apk-analysis/tsl9-v4160-clock-abi-2026-10-21/`; publication uses `analysis/v4160-clock-abi-2026-10-21/`. The fresh verifier needs only the current four C/header files, its local `elf32.py`, and LLVM. No ignored original-image build archives are required. The verified distribution is Android NDK 27.1.12297006, Clang 18.0.2, using RV32IMAC/ILP32, `-Os`, freestanding/no-relax flags and explicit per-unit reservations. Other compiler encodings outside this proof profile fail explicitly.

`check_compiler.py --project-root . --require-local-builds` performs a read-only replay of retained native and hosted receipts. Omitting the final flag reports missing archives explicitly and checks sealed metadata/current sources; it does not imply a fresh compile. The `probe_*.py` files document bounded Windows laboratory investigations with pinned local tool paths; `verify_compiler.py` is the portable fresh-build entrypoint. Build objects, ELF files, logs, and disposable candidates remain local.

Full original ABI, pointwise register behavior, IRQ compatibility, original placement, installed ROM, physical hardware, and Bluetooth OTA remain unproved. The old native image gate is unchanged. No firmware BIN is produced and no RV32 execution, ISA emulation, hardware I/O, or network operation occurs.
