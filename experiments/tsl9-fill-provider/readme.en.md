# Fill provider 0x8520

[繁體中文](README.md)

Candidate `[0x8520,0x85C8)` contains168 bytes/55 RV32 instructions. C owns constants, masks, arithmetic and volatile word/byte stores. Thirteen private architectural regions retain AUIPC, computed JALR, RA and control ordering; they are not independently C-callable functions.

- Short count n=0..15 dispatches to `0x8596-4*n`: zero returns directly; other paths store offsets n-1 down to0.
- Misalignment m=pointer&15 (1..15) first writes16-m prefix bytes through a computed JALR. T0 holds original RA and temporary RA is0x85BA. RA and pointer/count adjustments follow the return.
- Bulk stores words at+0/+4/+8/+12, advances16, then uses unsigned pointer<endpoint; the tail again stores bytes backwards. A normal count loop is not interchangeable under pointer wrap.
- A0/SP/S/GP are untouched. A1 expansion, A2 tail count, A4 tail base, A5 and T0 have conditional exit residues. Only the final-memory projection on valid ordinary nonwrapping memory is memset-like; no libc substitution was made.

Actual fill.v1 compilation was168B but LLVM swapped RA restoration and A5 adjustment. Selected fill.v2 only adds a LIVE constraint after the RA port, with unchanged flags; v1 source/measurements remain. Actual `build/verified-v1/{c,cpp}/verification.json` build and replay passed:13FUNC,8pending RELA,zero UND/global ABS. All nonrelocation bits and55 typed instructions match the original. Each language passed94 controls with full hash checks disabled:55 instructions,13 bindings,8 addends,13 IR ports and5 scalar/SSA/volatile changes.

[Composition evidence](../tsl9-tagged-native-chain/readme.en.md) additionally proves original-PC adjacency and 31 computed cases (16 unique destinations). Absolute AUIPC-derived T0/A3 residues change with placement; a VMA0 partial object is not an original-PC result.

The specific tagged caller supplies A0=SP+18,A1=0,A2=11. Its static path clears SP+28 down toSP+18 without changing SP/S0-S3. The following resident call remains unknown; this non-interference conclusion cannot extend through it.

```sh
python -B experiments/tsl9-fill-provider/verify.py --build --out-dir experiments/tsl9-fill-provider/build/local-v1 --llvm-bin "$LLVM_BIN"
python -B experiments/tsl9-fill-provider/verify.py --out-dir experiments/tsl9-fill-provider/build/local-v1 --llvm-bin "$LLVM_BIN"
```

Use an existing hash-matching Windows LLVM and a fresh first output folder. No target/ISA/host-model or hardware-I/O execution occurred. Ordinary ABI, asynchronous IRQ, physical memory, whole image and OTA compatibility remain unproved. **Reverse engineering remains incomplete; no flashable BIN.**
