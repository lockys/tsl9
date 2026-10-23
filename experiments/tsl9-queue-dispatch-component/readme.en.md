# Partial link of the queue consumer and genuine providers

[繁體中文](README.md)

This experiment uses existing LLVM `ld.lld -r --no-relax` to combine ten queue private architectural regions, seven filter regions, and two readable C providers. It introduces no fake provider, ABS address provider, wrapper function, or BIN.

`src/providers.c` uses two preprocessor renames and an ordinary include of the sealed small-provider C bodies. The status reads the V4.1.60 GP+167 byte; the clear uses unsigned comparison, pointer arithmetic and a volatile byte store. The unchanged small-provider profile is RV32IMAC/Zicsr, ILP32, Oz, no relaxation/outlining/unwind, fixed x1..x31 except A0/x10 and A5/x15. Modes are C11 and C++17 with C++ exceptions disabled. Actual MD closure contains the adapter, original C body and compiler stdint.h.

The checker measures 526 code bytes, 184 instructions and nineteen genuine FUNC symbols. Queue/filter/providers start at offsets 0/314/502; status and clear occupy 502..508 and 508..526. Diagnostic ET_REL VMA is zero. Official PCs identify source provenance, not physical placement of this partial link.

The independent composition parser checks every function, allocated section, all32 RELA records, original control operands and non-control bits, complete LLVM raw readback, and the frozen queue/filter SSA, typed operand, MD, command and compiler/resource proofs. Previously undefined `82d2`, `81aa` and `820c` references now bind to genuine C definitions. Six strong UND providers remain: `8a56`, `9454`, `9b36`, `12abe`, `12a08`, `14d2e`.

Symbol-level resolution does not apply the32 pending machine control immediates. The checker distinguishes C.JAL from C.J and preserves RA link semantics; original decoded immediate destinations must match the actual symbolic identities. Pending raw targets are never reported as executed resolved transfers. Actual in-memory ELF, operand, IR and MD regression controls must be rejected.

From the project root, set `LLVM` to the existing LLVM bin directory:

```sh
python experiments/tsl9-queue-dispatch-component/check.py
python experiments/tsl9-queue-dispatch-component/build.py --project-root . --llvm-bin "$LLVM" --queue-root experiments/tsl9-queue-consumer/build/verified-v3 --filter-root experiments/tsl9-queue-filter/build/verified-v1 --build-root experiments/tsl9-queue-dispatch-component/build/NEW
python experiments/tsl9-queue-dispatch-component/check.py --project-root . --llvm-bin "$LLVM" --replay experiments/tsl9-queue-dispatch-component/build/NEW/c/verification.json
```

Default mode validates source metadata only. `--folder MODE --receipt NEW` writes a create-only actual review; `--replay` is read-only. `--require-firmware-ready` must reject. The Python/POSIX wrapper has no personal hardcoded paths. The previously denied Windows Git Bash is not retried; sh runtime remains unverified.

The first C compile and link succeeded, but review stopped because the checker incorrectly expected nineteen address-significance bytes. The actual inputs contribute 10+7+0=17. `repair-history/` retains that checker and the original compile-receipt hash. Only this metadata derivation changed: original C artifacts and compile receipt remain unchanged without recompilation/relinking; C++ is compiled once with the same original recipe. This mechanical repair does not strengthen semantic claims.

Private regions are not independent ordinary C ABI functions. Three fresh indirect calls, external provider identities/ABI, original-placement AUIPC meaning, CSR/IRQ/asynchronous behavior, finite polling, resident ROM and hardware compatibility remain open. This is offline compiler/link/static evidence only: no target, ISA, MMIO, HOST behavior suite, network, complete firmware BIN, OTA or hardware flashing. Firmware-ready, installed-ROM and physical-placement gates remain false.
