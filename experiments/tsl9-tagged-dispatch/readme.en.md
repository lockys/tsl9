# Tagged-record transmit candidate 0x16B7C

[繁體中文](README.md)

C11/C++17 reconstruction of official ID2966 V4.1.60 range `[0x16B7C,0x16C72)`: 246 bytes, 86 RV32 instructions and 15 private architectural regions. C owns constants, arithmetic, masks and two volatile word loads. Explicit architectural ports preserve physical registers, memory order, frames and controls. These regions are not ordinary C-callable functions or a complete high-level source recovery.

## Confirmed

- Fresh record[11] accepts tags1/2; fresh [GP+84] pointer byte4 bit3 returns4 before allocating a frame.
- A64-byte frame saves RA/S0/S1/S2/S3 in original order. Initial length>8 takes the restoring return. Length is freshly read after opaque calls; the initial bound cannot be assumed to survive.
- Stack table bytes are0x30/0x40/0x50. Identifier bytes, length, payload arguments and store order match the original instructions.
- Five direct JALs reference four external providers. One C.JALR freshly loads [0x4004C], linking RA=0x16BFA. Subsequent ports observe then-live SP/S0-S3 without assuming a normal callee ABI.
- Busy handling increments S1 then tests S1!=S3. Final status &0x70 collapses to0/4. Cold blocks after RET are reachable.

## Static evidence

Local original receipts: `build/verified-v2/{c,cpp}/verification.json`. Each language actually ran five compile/IR/read/partial-link steps:15 FUNC,11 pending RELA,4 strong UND,0 global ABS. All nonrelocation bits and86 instruction widths, physical operands and order match the original. Pending machine control immediates remain; no fabricated ABS providers or whole246-byte equality are claimed.

Each language passed 132 negative controls with whole ELF/IR hash checking disabled: 86 raw instruction changes, 11 relocation-addend changes, 30 IR architecture-port changes and 5 C scalar changes. Separate checks cover full ELF/IR, source/tool identity, actual MD include closure, actual recipes and artifact hashes. Mutation coverage is not exhaustive for metadata or SSA wiring: defined-symbol bindings and SSA operand rewiring currently rely on complete ELF/IR digest rejection; normalized scalar rows check operation kinds and constants only.

Probe-v1 passed. Initial verified-v1 compiled successfully but the checker failed with `KeyError: portable` before formal receipts. The checker helper lookup was repaired; its original is retained in `history/verify.pre-portable-fix.py`. Source, flags and toolchain stayed unchanged. A fresh verified-v2 build and read-only replay passed; strict firmware gating returned1 as intended.

From the repository root, with an existing hash-matching Windows LLVM:

```sh
python -B experiments/tsl9-tagged-dispatch/verify.py --build --out-dir experiments/tsl9-tagged-dispatch/build/local-v1 --llvm-bin "$LLVM_BIN"
python -B experiments/tsl9-tagged-dispatch/verify.py --out-dir experiments/tsl9-tagged-dispatch/build/local-v1 --llvm-bin "$LLVM_BIN"
```

The output directory must be new. No downloads, target/ISA/host-model execution or BLE/CAN/UART/Flash operations occurred.

## Inference and gaps

The0x30/0x40/0x50 table, bit3 and0x70 flags support investigating a three-buffer transmit-register layout. Specific external silicon, board identity and controller count are unconfirmed. Global function extent and all external incoming references remain unproved.

Reliable providers for0x8520/0x168DE/0x1693E are missing. The separately reconstructed0x16994 reader was not linked into this candidate. Physical ROM identity at[0x4004C], complete ABI, original-PC placement, startup/IRQ/OTA and hardware behavior remain unknown. Existing1162-byte composition evidence is preserved; this candidate has not joined it.

A possible future diagnostic could retain distinct tag/global-disable/length/busy/raw-status failure reasons; no device behavior was changed here. **No flashable BIN; reverse engineering remains incomplete.**
