# OTA handler reduced to 568-byte shared C/C++

[繁體中文](README.md)

Using actual compiler IR and original shared exits, native C11/C++17 shrinks from 776 bytes / 285 instructions / a 112-byte frame to **568 bytes / 193 instructions / a 48-byte frame**. All eight register inputs/outputs, memory clobbers, volatile operations, U/S/W/R/E behavior and W reply projections remain. The original region is 530 bytes, leaving a 38-byte excess. **No link, BIN integration or flashability verification.**

## Actual source changes

The previous native `oh_port` placed its arguments and escaping two-byte response array in one object. A wrapper-owned `volatile uint8_t[2]` and a port pointer now separate their lifetimes, avoiding escape of the entire argument object through the reply pointer. This single change produced a measured intermediate 592 bytes / 196 instructions / a 48-byte frame.

Explicit C labels then share the small/packet/page terminal reply sites corresponding to original `0x9D7A`, `0x9DB4` and `0x9DF4`. Shared source and an independent fixture check setter order, per-command masks, source PCs and stopping behavior. Final objects retain nine true undefined symbols and 20 relocations: twelve JALs and four HI/LO pairs, plus one indirect slot `0x4004C` call. No numeric ABS providers, stubs, fake FUNC extents or original instruction fallback. [Static assembly observations](allocation-observations.json) record111 SP-addressed memory instructions before and23 after; these include saves, restores and response accesses, not dynamic cost or removable-spill counts.

[Shared C/C++](../../experiments/tsl9-v4160-ota-handler-compact/readme.en.md), [implementation](implementation/readme.en.md), [independent HOST/native and source-delta review](ABI-review/readme.en.md), [UID/candidate copy callees](callee-review/readme.en.md), and [plan](plan.en.md).

## Negative result and previous erratum

The previous three analysis READMEs incorrectly describe four unrolled quarter callsites. Actual 776-byte objects have one quarter JAL and a backedge; sealed independent ABI metadata also records one. The no-unroll probe still produces 776 bytes / 285 instructions. The ineffective pragma is absent from final sources, without a compiler-flag search to force fit. See the [erratum](../v4160-ota-handler-2026-10-22/ERRATA.md) and new independent evidence. Historical sealed files remain unchanged.

The old parent seal also binds six previous root/milestone documents. After this authorized documentation update, its historical global-document check is not advertised as passing against current root documents. Sealed members and program sources are unchanged, and the old checker is not weakened. All six original document hashes remain reproducible at `ea92e46`; see [historical context](baseline-context.json). This milestone binds versioned scope/program evidence instead of mutable root documents.

## Evidence limits

HOST executes our own C/C++ with synthetic memory and callee providers, after an immutable executable machine guard. No RV32 executes or is emulated. Native checks read actual ELF/IR/MD, all instructions and source/tool identities. Intermediate probe summaries preserve source identities; unavailable build paths are not advertised as portable replays.

The App UID comparator requires length14, obtains bytes through its builder and fresh slot `0x4004C`, then returns0/1. Two official ROM candidate copy leaves support conditional input/preservation contracts, without identifying installed ROM. No ambient registers are dropped from a merely local non-read observation.

The private C reply is not original live SP+12. Actual new reply bytes occupy SP+6/7, while ten slots save RA and S0..S8; SP+12 already saves S7 and must not be blindly reused for the reply. Matching a 48-byte frame does not prove save positions, scratch, S/SP/RA/GP, aliases or asynchronous observers. The remaining 38 bytes, live ingress/continuations and complete-image layout still require work.

Complete TX image SHA-256 `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89` remains unchanged: thirteen original regions totaling930 bytes come from readable C/C++ and an explicit ABI layer. That is not feature completion, and separate components are not added to integrated coverage. See the [full hardware/ROM/BOOT/IRQ/Flash/BLE OTA/recovery audit](../v4160-ota-handler-2026-10-22/status.en.md). Offline packet preflight and wait-reason diagnostics remain proposals.

## Rerun

```sh
python3 -B experiments/tsl9-v4160-ota-handler-compact/verify_host.py --project-root /absolute/re-tsl9 --language both --build-root /absolute/re-tsl9/experiments/tsl9-v4160-ota-handler-compact/build/new-host
python3 -B analysis/v4160-ota-handler-compact-2026-10-22/implementation/verify_native.py --project-root /absolute/re-tsl9 --tool-dir /absolute/llvm/bin --language both --build-root /absolute/re-tsl9/experiments/tsl9-v4160-ota-handler-compact/build/new-native
```

Outputs are create-only. Scopes distinguish default metadata checks from explicit actual-artifact replays. Windows is the measured environment; Python/POSIX shell entrypoints do not establish Linux/macOS execution.
