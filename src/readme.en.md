# Selected reverse-engineered C/C++ source

[繁體中文](README.md) · [English](readme.en.md)

This directory is the working entry point for the readable source with the strongest currently available evidence. It contains 44 C/header files. The same C source is compiled separately as C11 and C++17 using the recorded profiles. Original experiments and frozen evidence remain in `experiments/` and `analysis/`.

| Directory | Contents | Evidence boundary |
| --- | --- | --- |
| [native/init_mask](native/init_mask/init_mask.c) | V4.1.60 initialization-tail register mask | Whole 30-byte function equals the official BIN; complete startup and physical placement unproved |
| [native/irq/irq_flag.c](native/irq/irq_flag.c) | Vector-slot39 status/flag handler | Complete76B/21i equals official16FB6; two fresh status reads/byte updates and MRET retained; original IRQ context and peripheral identity unproved |
| [native/irq](native/irq/interrupt_registers.c) | Four register helpers and IRQ initialization | Four helpers match at30B each; initializer normal outputs reviewed,180B vs original144B, asynchronous equivalence unproved |
| [native/timer](native/timer/delay.c) | V4.1.60 delay register contract | Entire54-byte leaf matches official; separate TU, not substituted into NV callback/OTA BIN |
| [native/nv/nv_write_frame_contract.c](native/nv/nv_write_frame_contract.c) | New NV write frame/fresh-source contract | Original32B frame/source slot and first40B outside JALs match; earlier LI0 leaves fault/IRQ gap |
| [native/nv/nv_read_registers.c](native/nv/nv_read_registers.c) | NV read register contract | 30B/14 instructions; no added wrapper A3 write or RA scratch; original has13 instructions, ordering/provider gaps remain |
| [native/nv/nv_read_live_count.c](native/nv/nv_read_live_count.c) | NV read with original count live | 30B/13 instructions; direct A2 shift and exact original10B call window; frame/return order and installed provider remain unproved |
| [native/nv](native/nv/nv_write_callback.c) | NV read/write, timer and Flash helpers | Includes both A1 clobber repairs; write frame/source reload, timer outputs and indirect providers remain limited |
| [native/adc](native/adc/caller_bank.c) | Caller-specific ADC setup and real volatile ports | Preserves the known live register bank; new16B frame and alias/IRQ constraints remain |
| [native/clock](native/clock/clock_query.c) | Improved clock-query/field register results | Fields normal outputs reviewed; full query branch semantics unproved,196B vs174B |
| [native/clock/clock_init.c](native/clock/clock_init.c) | BOOT/Runtime clock initialization | 232B/93i, entry falls through to C body; original cold tail and full IRQ/ABI/hardware remain unproved |
| [native/startup/init_writes.c](native/startup/init_writes.c) | Ordered initialization writes called from9250 | Whole40B/15i equals the official9F4C leaf; five volatile word writes, only A4/A5 modified; peripheral identity and full startup unproved |
| [native/startup](native/startup/reset_memory.c) | Runtime reset memory/CSR handoff | Reset138B/38i + clock232B retains RA18724 without next-function overlap; vector/main/resident and cold/indirect entries remain unresolved |
| [native/resident](native/resident/native.c) | SDK-candidate compare/fill/copy | Normal memory projection only; installed ROM identity, scratch/fault behavior and sizes remain unresolved |
| [reference/v4100](reference/v4100/dnd_actions.c) | DND, general settings and GATT framing models | V4.1.00 behavior references with unresolved providers; separate from V4.1.60 native source |

[source-manifest.json](source-manifest.json) records every origin, original/curated SHA256, individual include adaptations, the two A1 declaration repairs, and each compile entry's evidence and limits. The newer volatile-source experiment still has frame/slot differences and remains in experiments.

## Getting started

From the repository root:

```sh
python3 scripts/verify-curated-source.py
```

Default mode checks source provenance and inventory without LLVM. On Windows, use `py -3` or an installed `python` instead of `python3`.

To compile with an existing RISC-V-capable LLVM installation:

```sh
python3 scripts/verify-curated-source.py --tool-dir "/absolute/path/to/llvm/bin"
```

The script selects eighteen native translation units, compiles the original and curated versions as C11/C++17, and compares every function, allocated section and relocation in the resulting objects. Included C cores are emitted through their owning entry unit; compiling every `.c` as an independent link unit would duplicate definitions. V4.1.00 references are outside this native-object compilation, and no legacy HOST matrix was rerun.

The Windows run with Android NDK27.1.12297006/LLVM18 passed36 comparisons. Its local receipt is `build/curated-source/init-and-irq-leaves-20261023-v1/verification.json`. The Python entry uses only the standard library; other operating systems were not tested. A different toolchain must pass the same checks. No tools are downloaded and no compiler-flag search is performed.

Replay an existing result without compiling:

```sh
python3 scripts/verify-curated-source.py --replay "/absolute/path/to/verification.json"
```

**This source collection and offline evidence are not a complete firmware build.** Physical chip identity, installed ROM, memory ownership, complete startup/IRQ behavior and BLE OTA compatibility remain unproved. Successful flashing and execution of rebuilt firmware on the original hardware have not yet been verified. The script executes neither RV32 nor MMIO and produces or flashes no firmware BIN.

The [reset/clock composition](../experiments/tsl9-runtime-reset-clock-fit/README.md) separately checks linked adjacency, original call/RA, IR and negative controls. Earlier receipts remain local snapshots; their frozen verifiers may reject this newer source revision.
