# NV read: keep the original count live
[繁體中文](readme.zh-TW.md) · [English](readme.en.md)

This component extends the [30-byte/14-instruction candidate](../tsl9-nv-read-registers/readme.en.md). A genuine C uint32 shift and minimal register/call ports remove the destructive A1 shift followed by an A2 move. Curated source: [src/native/nv/nv_read_live_count.c](../../src/native/nv/nv_read_live_count.c).

## Measured result

Both C11 and C++17 objects and linked components contain **30 bytes /13 instructions**, code SHA256 `05b184cb6e192355342a6b6e71a7db136f2d53aa7aa33a341fb1551f4b49f58a`. The original also has30B/13 instructions, but **whole-function equality remains false**; original SHA256 `e9e2a0f4b50184fa5c7b37ee004867f393b8c960fe9e66e81dc40af897114f62`.

Relative offsets `[12,22)` exactly match the original10-byte sequence: `SLLI A2,A1,2; MV A1,A0; MV A0,A4; JALR A5`. The wrapper adds no A3 write, RA source scratch, or destructive pre-call A1 shift. The opaque callee may still change its declared caller-saved registers.

A fixed-A2 empty ASM boundary alone constrains where the computed result ends up, rather than the C shift's destination. The new ports add real SSA dependencies: destination must first reach A4; unshifted A1 remains live before the C shift reaches A2. ASM does not implement the arithmetic, carry copied function bytes, or supply a fake provider. Unsigned32-bit count wrapping remains intact.

Each invocation freshly reads32 bits from0x4004C. At the call boundary: A0=entryA2, A1=entryA0, A2=u32(entryA1<<2), A4=entryA2, A5=fresh slot value. Failure of the unknown provider to return normally does not fabricate result zero.

## Remaining gaps

- Original slot read precedes frame creation/RA save; candidate saves the frame/RA first. The A4 move also occurs in a different order relative to RA save.
- Original restores RA before setting A0=0; candidate sets zero first.
- Installed slot/provider identity, complete ABI, faults, IRQs, stack aliases, ROM, startup and physical compatibility remain unproved.
- Static UND/RELA/globalABS zero does not identify the dynamic provider. Equal size is not physical placement or flashability proof.

## Offline verification

From the project root, supply the original BIN, existing LLVM and a new build directory:

```sh
python3 experiments/tsl9-nv-read-live-count/verify.py --project-root . --tool-dir "/absolute/LLVM/bin" --firmware "/absolute/ID-2966-V4.1.60-decoded.bin" --build-root "/absolute/project/experiments/tsl9-nv-read-live-count/build/new-run"
python3 experiments/tsl9-nv-read-live-count/verify.py --project-root . --replay "/absolute/project/experiments/tsl9-nv-read-live-count/build/component-v2/c/verification.json"
```

Windows may use `py -3` or `python`. Actual tools were Windows Android NDK27.1.12297006/LLVM18. The verifier pins tools, stdint, source, linker, original image and operand ledger; it reads actual compiler MD dependencies, IR value flow, complete ELF allocations and LLVM raw disassembly. Other platforms were not tested. These static checks execute neither ISA nor MMIO, and are not independent CPU semantics proof.

Final receipts are `build/component-v2/{c,cpp}/verification.json`. Native-v1 only kept originalA1 live: LLVM introduced A3 scratch and32B, so it was rejected; that build retains a source snapshot. Native-v2 adds the A4-to-A1 ordering dependency and produces the accepted result. Component-v1 retained a C++ `noundef` IR parsing failure; explicitly accepting that qualifier allowed component-v2 to pass. Old outputs remain historical snapshots rather than claims of replayability with the current verifier.

No new OTA BIN, flashing or physical hardware operation occurred.
