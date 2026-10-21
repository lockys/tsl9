# Actual 144-byte C/C++ callframe main

Fresh C11 and C++17 builds both produce **144 bytes / 46 instructions** for the initializer and **four 30-byte / 12-instruction helpers**, totaling **264 allocated bytes / 94 instructions**. All five functions link at their original addresses: main 0x9A42 and helpers 0x19124/0x19142/0x19160/0x1917E. The component has no extra allocated metadata, writable state, hidden functions, aliases or final undefined symbols. C++ explicitly adds the already tested `-fno-exceptions` profile; no new optimization/profile search was performed.

The first SP adjustment and **every byte from main offset 10 onward** equal the original image at the same addresses. All original instruction boundaries remain. All **120 helper bytes** also equal the original. Only the four two-byte prologue stack saves differ:

| Store order | Original | Compiled C/C++ |
|---:|---|---|
| 1 | S2 → SP+0 | RA → SP+12 |
| 2 | RA → SP+12 | S0 → SP+8 |
| 3 | S0 → SP+8 | S1 → SP+4 |
| 4 | S1 → SP+4 | S2 → SP+0 |

The save multiset and 16-byte frame roles match, but the stores occur in a different order at 0x9A44/0x9A46/0x9A48/0x9A4A. **Exact main byte identity, original pointwise equivalence and asynchronous/interrupt equivalence remain false/unproved.** This is an observable stack-write ordering difference before the CSR clear. Scoped function-size/address fit is true; it does not prove a safe drop-in replacement, complete original ABI, full-image integration or physical/OTA compatibility.

The checker validates the immutable original264-byte/94-instruction source seal and the original callframe-plan seal, then uses the pinned raw operand decoder independently of objdump. Every instruction row is bound to the actual ELF bytes and complete extent, including both helper return regions. Only the original main/helper destination-register sets are permitted. The standalone helpers have no A1/SP/T0/A2/A3 writes.

All six calls are actual **four-byte JAL with RD=RA**, at the original PCs and targets, with RA=PC+4 pointing to an original continuation boundary. The main object records exactly six `R_RISCV_JAL` relocations at those offsets and exactly four explicit helper undefined obligations; the final linked ELF resolves them all. There are no invented absolute providers or call stubs. The body comparison also confirms the original CSR sources, live mask additions, PFIC instructions, final RET and balanced SP adjustments.

The tail performs the original **fresh frame loads** into RA/S0/S1/S2 from live SP+12/+8/+4/+0. These are not replaced by saved input snapshots. Equality with incoming registers requires the saved words to remain unchanged; SP restoration similarly depends on the live frame base. The recorded normal-output contract retains those conditions. This static proof does not execute calls, load target RAM, emulate CSR state or claim interrupt-state equivalence. IR checks separately verify six ordered explicit call primitives and their A0/A1/RA/A4/A5/memory constraints, two live-S2 CSR boundaries and six PFIC store widths. They are structural IR checks, not a claimed full IR semantic executor.

Each language has **six actual compiled and linked source controls**, all rejected: missing RA clobber, wrong JAL link register, wrong first call target, wrong final flag, wrong PFIC width and wrong helper offset. Thirty additional transcript controls per language reject missing/altered/truncated/unparsed rows across all five functions. Neither valid components nor negative controls are executed.

```sh
python analysis/v4160-irq-callframe-2026-10-21/compiler-review/verify_callframe.py --project-root . --tool-dir /path/to/llvm/bin --language both
sh analysis/v4160-irq-callframe-2026-10-21/compiler-review/verify_callframe.sh --project-root . --tool-dir /path/to/llvm/bin --language both
python analysis/v4160-irq-callframe-2026-10-21/compiler-review/check_callframe.py --project-root .
```

In the original analysis workspace use `apk-analysis/tsl9-v4160-irq-callframe-2026-10-21` instead of `analysis/v4160-irq-callframe-2026-10-21`. Dependency lookup supports both layouts by exact content hash. Individual `--clang`, `--linker`, `--objdump` and `--firmware` overrides are supported. The existing offline firmware resolver checks explicit input, workspace exports and the published firmware-downloads path, always requiring exact original image hash. No old build archives are needed: only the frozen five source/header inputs, pinned prior tool/parser/original-source/plan evidence, original image and local LLVM tools. The direct Python CLI was verified on Windows; the POSIX launcher is source only and was not run through WSL/Git Bash.

`results.json` selects two byte-identical metadata receipts outside `build/`. The read-only checker validates sealed metadata/current source pins and replays local artifacts when present. Add `--require-local-builds` to require the selected historical archives. Metadata checking is not fresh compilation. All compiled ELF/IR/log/control sources remain local; no firmware BIN, full-image patch, target execution, ISA emulation, network or device operation occurs. Original/model/previously sealed files and P/D checkouts remain unchanged by this review.
