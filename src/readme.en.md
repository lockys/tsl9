# Selected reverse-engineered C/C++ source

[繁體中文](README.md) · [English](readme.en.md)

This directory is the working entry point for the readable source with the strongest currently available evidence. It contains 52 C/header files. The same C source is compiled separately as C11 and C++17 using the recorded profiles. Original experiments and frozen evidence remain in `experiments/` and `analysis/`.

| Directory | Contents | Evidence boundary |
| --- | --- | --- |
| [native/init_mask](native/init_mask/init_mask.c) | V4.1.60 initialization-tail register mask | Whole 30-byte function equals the official BIN; complete startup and physical placement unproved |
| [native/irq/irq_flag.c](native/irq/irq_flag.c) | Vector-slot39 status/flag handler | Complete76B/21i equals official16FB6; two fresh status reads/byte updates and MRET retained; original IRQ context and peripheral identity unproved |
| [native/irq/flag_consumer.c](native/irq/flag_consumer.c) | GP flag consumer at17002 | Entry8B/body54B; all54B outside two unresolved JAL windows match official; partial-link adjacency checked separately, receive/provider ABI remains open |
| [native/receive](native/receive/receive_wrapper.c) | Receiver entry16B0A and tail register write | Entry14B/body56B;54 non-call bytes match,4 open JALs; physical S0/S1/frame ports retain live state without an added C frame; downstream ABI remains open |
| [register read](native/receive/register_read.c) / [write](native/receive/register_write.c) | GPIO selection,32B frames and three SPI transfers | Read72B/write76B,non-call60B/64B match original; fresh slots and RA-before-cleanup retained; individual objects retain open SPI calls, with genuine definitions bound in the separate352B partial link |
| [SPI transfer](native/receive/spi_transfer_ports.c) | SPI polling/data leaf | Eight machine regions and five RVC ports; separate nominal link matches all72B/25i, not ordinary C ABI or hardware proof |
| [packet receive](native/receive/packet_receive.c) | Packet reception, DLC/ID and shared exit | 142B/52i across14/116/12B regions;120 noncontrol bytes match; four JALs and two finish branches remain pending; private ABI, hardware and flashing unproved |
| [ring insert](native/receive/ring_insert.c) | Receive queue and fresh resident indirect call | Five private regions; nominal92B/32i entirely matches original. PC-derived table and physical post-call S0/S1 retained; resident identity, caller bounds and hardware unproved |
| [ring IRQ adapter](native/irq/ring_irq_adapter.c) | Conditional frame and two MRET paths | 52B/17i;42 original noncontrol bytes, three pending edges and two UND providers; then-live SP ports, full IRQ/provider ABI unproved |
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

The script selects twenty-six native translation units, compiles the original and curated versions as C11/C++17, and compares every function, allocated section and relocation in the resulting objects. Included C cores are emitted through their owning entry unit; compiling every `.c` as an independent link unit would duplicate definitions. V4.1.00 references are outside this native-object compilation, and no legacy HOST matrix was rerun.

The fresh Windows build with Android NDK27.1.12297006/LLVM18 passed52 comparisons (104 objects). Its receipt is `build/curated-source/ring-irq-20261023-v2/verification.json`; the earlier SPI curation receipt remains historical. The Python entry uses only the standard library; other operating systems were not tested. A different toolchain must pass the same checks. No tools are downloaded and no compiler-flag search is performed.

Replay an existing result without compiling:

```sh
python3 scripts/verify-curated-source.py --replay "/absolute/path/to/verification.json"
```

**This source collection and offline evidence are not a complete firmware build.** Physical chip identity, installed ROM, memory ownership, complete startup/IRQ behavior and BLE OTA compatibility remain unproved. Successful flashing and execution of rebuilt firmware on the original hardware have not yet been verified. The script executes neither RV32 nor MMIO and produces or flashes no firmware BIN.

The [reset/clock composition](../experiments/tsl9-runtime-reset-clock-fit/README.md) separately checks linked adjacency, original call/RA, IR and negative controls. Earlier receipts remain local snapshots; their frozen verifiers may reject this newer source revision.

The [SPI component and pipeline](../experiments/tsl9-spi-transfer-leaf/README.md) separately verify resolved leaf bytes and352B ET_REL linkage. This source-copy check does not resolve those architectural edges itself.

The [packet component](../experiments/tsl9-packet-receive/README.md) has an independent verifier; its formal local receipts are `experiments/tsl9-packet-receive/build/verified-v2/{c,cpp}/verification.json`. Source curation itself resolves neither the six control transfers nor the provider/IRQ ABI.

The [ring and original-layout receive graph](../experiments/tsl9-ring-insert/README.md) distinguishes a resolved local code graph from an unknown dynamic resident provider and full firmware readiness.
