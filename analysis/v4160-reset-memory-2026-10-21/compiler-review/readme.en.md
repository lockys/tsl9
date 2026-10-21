# Reset-memory native compiler evidence

The frozen C/header have been compiled as actual RV32 C11 and C++17 using only T0/A0/A1/A2 as allocator registers. The new leaf is **78 bytes / 24 instructions**; the optional fragment is **80 bytes / 24 instructions**. The captured original memory slice `0x186BA..0x186F8` is **62 bytes / 17 instructions**. Both new forms fail the original slot-size gate. Structural compiler checks passing does not mean original placement or firmware compatibility passed.

The leaf is a new callable interface with RET. The original memory slice falls through to `LI T0,31` and CSR initialization. Its final old copy-word T0 is immediately overwritten there; this component does not promise the same T0 residue or prove entry/IRQ compatibility. Final A0/A1/A2 commitments are present in the shared C and validated by separate hosted tests. Full native loop and pointwise register semantics remain unproved.

The native CFG contains two loop SCCs: forward interleaved word copying and zero word stores. Both loops retain unsigned tests. Every actual ELF instruction byte, boundary, destination field, and internal branch/fallthrough is checked. Only the original scratch subset may be written; no SP/GP write, stack access, hidden memcpy/memset/runtime call, writable allocation, or fake original symbol is accepted. The loop CFG is deliberately cyclic: the checker does not infer termination for altered GP domains or add a timeout to the C function.

LLVM IR has three separate empty-asm GP observations with memory clobbers, one volatile READ32 site and two volatile WRITE32 sites. Actual baseline machine code mentions GP four times because Clang rematerializes the zero-loop pointer after its entry guard. Therefore these results are bounded to the normal fixed-GP environment and do not establish pointwise GP snapshots or asynchronous GP mutation behavior. One explicitly authorized diagnostic clear-step barrier reduced physical GP uses to three, but the code remained 78 bytes; the diagnostic was not adopted and the parent C/header stayed unchanged.

## Fragment continuation is still missing

The optional source contains `c.j __tsl9_reset_resume_186f8`, but this Clang assembler actually emits a **four-byte JAL x0**, with one `R_RISCV_JAL` relocation (type 17, offset 76). No compressed two-byte jump is claimed. The fragment object retains exactly that undefined continuation symbol. A strict link without a continuation provider is actually rejected.

A separate `ADDRESS-WITNESS-ONLY.elf` binds the symbol numerically to `0x186F8`, while placing the new helper at diagnostic base `0x1000`. This avoids overlap and supplies no continuation implementation. Placing the 80-byte candidate at original `0x186BA` would overlap `0x186F8` with the candidate's own bytes; that original-placement gate explicitly fails. No misleading original-slot witness or firmware BIN is produced.

Each of the four configurations actually compiles, links, and rejects three controls: an A3 write, an SP write, and incorrect word-store width. Six transcript controls per configuration reject missing first/interior/final rows, changed instruction bytes, and unparsed interior/trailing lines. Four byte-identical selected receipt JSON files are shipped under `receipts/`; executable objects, IR, ELF files, and logs remain in the investigation workspace only. `results.json` records original artifact paths and hashes for audit, not a promise those old paths exist in every checkout.

## Fresh build and read-only check

Python 3.10+ and local LLVM RV32IMAC tools are required. The portable entrypoints, from a published checkout, are:

```sh
python3 analysis/v4160-reset-memory-2026-10-21/compiler-review/verify_native.py \
  --project-root . --tool-dir /path/to/llvm/bin --language both
python3 analysis/v4160-reset-memory-2026-10-21/compiler-review/verify_native.py \
  --project-root . --tool-dir /path/to/llvm/bin --language both --fragment
```

Alternatively use `--clang`, `--linker`, and `--objdump`. The investigation prefix is `apk-analysis/tsl9-v4160-reset-memory-2026-10-21/`; publication uses `analysis/v4160-reset-memory-2026-10-21/`. Only the current two C/header files, local `elf32.py`, and LLVM are needed for a new compile. The verified tools are Android NDK 27.1.12297006, Clang 18.0.2, with RV32IMAC/ILP32, `-Os`, freestanding/no-relax flags and explicit reservations for every other integer register. Unsupported compiler output fails explicitly.

`check_native.py --project-root .` checks the seal, current sources, verifier/parser, and all four selected historical receipt metadata files. It explicitly reports missing old build archives. `--require-local-builds` additionally requires and replays those historical artifacts; these archives are intentionally not shipped. A metadata-only check is not a new compilation. Fresh builds create their own UUID directories and actual receipts.

No original/rebuilt RV32 code is executed or ISA-emulated; no device I/O or network action occurs. Original reset fallthrough/IRQ ABI, ROM services, memory mapping, physical hardware, fixed placement, and Bluetooth OTA remain unproved. The old full native image gate is unchanged.
