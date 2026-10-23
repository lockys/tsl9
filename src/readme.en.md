# Selected reverse-engineered C/C++ source

[繁體中文](README.md) · [English](readme.en.md)

This directory is the working entry point for the readable source with the strongest currently available evidence. It contains 66 C/header files. The same C source is compiled separately as C11 and C++17 using the recorded profiles. Original experiments and frozen evidence remain in `experiments/` and `analysis/`.

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
| [IRQ provider](native/receive/irq_provider.c) | Fresh word reads and receive-data fields | Six18/8/108/10/10/10B regions; full164B/53i nominal code equals original, retaining A4/A5 effects and two RETs; physical MMIO/IRQ/silicon unproved |
| [queue consumer](native/receive/queue_consumer.c) | Queue release and conditional dispatch | 314B/107i across10 private regions;230 complete noncontrol bytes and2163 retained bits match;25 pending RELAs/eight UND remain, with physical SP/S-register/CSR and resident residue ports; not full firmware |
| [record program](native/receive/record_program.c) | 93AA–94EE record setup and control | Four routines324B/109i,19 architectural regions; complete nominal code equals original in C/C++. Opaque40068/40070 do not imply an installed allocator ABI, valid memory or bounded post-call indices |
| [GP word toggle](native/receive/gp_word_toggle.c) | 9B36 byte guard and word XOR2 | All24B/7i match; only A4/A5 written, skip retains A4. Physical purpose, GP/memory validity and IRQ/OTA remain unknown |
| [queue leaves](native/receive/queue_small_providers.c) | V4.1.60 status and bounded clear | Fully original-equal6/18B C leaves; fresh GP+167 byte, unsigned index<=2 byte clear; no spills/UND/relocations. Diagnostic VMA0 only; actual consumer composition and hardware remain open |
| [queue filter](native/receive/queue_filter.c) | Packaging/forwarding gate at82D2 | 188B/69i,166 whole noncontrol bytes match;7 pending edges with one real C.JAL provider. Then-live frame/S-register state retained; nonzero is not forwarding success |
| [transport frame](native/receive/transport_frame.c) | 8A56 admission, frame, copy and checksum | 280B/96i,246 whole noncontrol bytes match;9 local pending RELAs/0 UND. Fresh4013C admissions and40050 tail provider remain unknown; post-call length is not bounded by the initial guard |
| [record dispatch](native/receive/record_dispatch.c) | 12A08 status/ID/tag/copy/peripheral dispatch | 102B/35i across9 private regions;4 genuine UND/9 pending RELAs. Then-live SP/S0/call residues retained; full provider ABI and hardware remain open |
| [record predicate](native/receive/record_predicate.c) | 821E pointer-bit/index/byte predicate | Complete42B/15i original-equal C/C++; no frame/stores/calls/UND/relocations. GP/memory/flag meaning and hardware unproved |
| [fill provider](native/receive/fill_provider.c) | 8520 byte/word fill and computed jump table | Thirteen private regions168B/55i,eight pending controls/no UND. Descending SB table,word order,unsigned pointer loop and RA/T0 retained; computed targets/exit residues require original-PC placement. No libc substitution or hardware proof |
| [SPI command providers](native/receive/spi_write_providers.c) | 168DE buffer path and1693E command path | Twenty private regions182B/68i;13pending controls/one genuine16896 provider reference.32B frames,fullwidth fresh slots,zero-length pre-test,GPIO word writes and RA restore ordering retained; physical transmission and OTA unproved |
| [tagged dispatch](native/receive/tagged_dispatch.c) | 16B7C tagged path,64B frame and record handling | Fifteen private regions246B/86i;11pending controls/four genuine UND. Early returns,then-live SP/S0-S3,opaque residues and inequality loop retained. Independent native proof checks original fixed bits/symbolic destinations; provider ABI,hardware and OTA remain open |
| [peripheral write](native/receive/peripheral_write.c) | 18CA4 selected-bank ID/length/payload writes | Seven private regions,212B/72i nominal code entirely original-equal. Three fresh status reads, ordered22 static loads/eight stores and exit residues retained; physical peripheral/ABI/OTA unproved |
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
| [resident copy architecture](native/resident/copy_arch.c) | WCH V1.31 SDK candidate copy | Full58B/18i matches candidate at conditional RAM20000332; preserves T0/A7 and fault-prefix ordering. Installed TSL9 resident identity remains unknown; not linked into firmware |
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

The script selects 40 native translation units, compiles the original and curated versions as C11/C++17, and compares every function, allocated section and relocation in the resulting objects. Included C cores are emitted through their owning entry unit; compiling every `.c` as an independent link unit would duplicate definitions. V4.1.00 references are outside this native-object compilation, and no legacy HOST matrix was rerun.

The fresh Windows build with Android NDK27.1.12297006/LLVM18 passed80 comparisons (160 objects). Its receipt is `build/curated-source/record-program-20261023-v1/verification.json`; the earlier curation receipts remain historical. The Python entry uses only the standard library; other operating systems were not tested. A different toolchain must pass the same checks. No tools are downloaded and no compiler-flag search is performed.

Replay an existing result without compiling:

```sh
python3 scripts/verify-curated-source.py --replay "/absolute/path/to/verification.json"
```

**This source collection and offline evidence are not a complete firmware build.** Physical chip identity, installed ROM, memory ownership, complete startup/IRQ behavior and BLE OTA compatibility remain unproved. Successful flashing and execution of rebuilt firmware on the original hardware have not yet been verified. The script executes neither RV32 nor MMIO and produces or flashes no firmware BIN.

The [reset/clock composition](../experiments/tsl9-runtime-reset-clock-fit/README.md) separately checks linked adjacency, original call/RA, IR and negative controls. Earlier receipts remain local snapshots; their frozen verifiers may reject this newer source revision.

The [SPI component and pipeline](../experiments/tsl9-spi-transfer-leaf/README.md) separately verify resolved leaf bytes and352B ET_REL linkage. This source-copy check does not resolve those architectural edges itself.

The [packet component](../experiments/tsl9-packet-receive/README.md) has an independent verifier; its formal local receipts are `experiments/tsl9-packet-receive/build/verified-v2/{c,cpp}/verification.json`. Source curation itself resolves neither the six control transfers nor the provider/IRQ ABI.

The [ring and original-layout receive graph](../experiments/tsl9-ring-insert/README.md) distinguishes a resolved local code graph from an unknown dynamic resident provider and full firmware readiness.

The [receive/dispatch/transmit integration](../analysis/receive-transmit-chain-2026-10-23/README.md) freshly compiles12 existing src units. Its9 original-PC spans reproduce1588B/555 instructions with no static UND; the full1902B partial component retains four genuine providers missing. Six opaque resident transfers and66970B of RX gaps remain unproved, so neither component is firmware-ready.

[9B36 source integration](../analysis/gp-word-toggle-2026-10-23/readme.en.md) extends the diagnostic partial link to1926B/669 instructions/108 strong FUNC/97 pending RELA/3 UND, binding13 current source units. The1588B nominal-address graph remains unchanged. The fixed-body v3 proof passes1991 negative controls per language; physical purpose and full hardware/OTA compatibility remain unproved.

[Record setup/control integration](../analysis/record-program-2026-10-23/readme.en.md) extends the genuine partial component to2250B/778i/127FUNC/109pending RELA/2UND (12ABE,14D2E). Eight resident transfers remain opaque; VMA0 AUIPC values are not executable original placement. Version2 passes2600 static negatives per language. No full-firmware or hardware/OTA claim is made.
