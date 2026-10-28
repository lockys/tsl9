# Lookup mode and three reconstructed DATA rows

[繁體中文](README.md) · [Project](../../readme.en.md)

Follow-up:48B now have [curated SRC/original-coordinate integration](../tsl9-lookup-mode-integration/readme.en.md),bringing coverage to95.60%. The evidence below retains this earlier unintegrated stage.

The whole original setter `0xD07C..0xD0EE` has a32-bit store at `0xD0C8`. Its three reaching literal definitions write `[1,5,0,1]`, `[1,4,0,1]` or `[1,2,0,1]`. Lookup mode is byte `0x2000BF39`; the separate phase byte at `0x2000BF3A` receives `rem 3`.

Given that this store completed before the normal consumer entry, the mode remains unchanged, caller memory is valid and the record buffer does not alias the fixed state, the `0xCEDC..0xCF96` consumer reads `0x1A078 +16*mode+nibble` at `0xCF5A`, with mode in `{0,2,4,5}` and nibble in `0..15`. This is conditional evidence, not a whole-program mode invariant.

|Mode|Original read window (exclusive end)|Treatment|
|---|---|---|
|0|`0x1A078..0x1A088`|Already backed by the final16 bytes of a432-byte readonly owner|
|2|`0x1A098..0x1A0A8`|New separate16-byte C/C++ DATA row|
|4|`0x1A0B8..0x1A0C8`|New separate16-byte C/C++ DATA row|
|5|`0x1A0C8..0x1A0D8`|New separate16-byte C/C++ DATA row|

[`lookup_mode_rows.v1.c`](lookup_mode_rows.v1.c) reconstructs only48 selected bytes. It adds no rows1/3, full-table declaration or `1A078` provider alias. Each selected row has a constant XOR offset to existing row0; that shape alone does not identify a complete algorithm or purpose.

[`verification-v1.json`](verification-v1.json) records all300 original function bytes, original/native equality, whole CFG/stack checks, store reaching definitions, actual C11/C++17 compilation and independent ELF reader agreement. Each new ET_REL object contains48 readonly DATA bytes and3 positive OBJECT symbols, with zero CODE, relocations, named UND or ABS providers. No target, HOST model or emulator is executed.

[`composition-v1.json`](composition-v1.json) additionally proves an actual partial link with the existing APP component:69,412 CODE bytes,3,962 existing DATA bytes and48 new DATA bytes, totaling73,422. Every input allocated-section byte, global symbol and typed relocation is retained. C/C++ results are identical and all six compiler UND remain. This is an ET_REL object without original-address integration.

[Feature candidate](feature-candidates.json): show lookup mode, phase and provenance conditions separately in offline diagnostics. This avoids treating `rem 3` as a mode bound; it is not implemented.

At this archived stage,the experiment was not curated into the formal `src/` manifest or linked at original APP addresses. Formal coverage then remained **95.54% (73,374/76,800 bytes)** and six compiler UND remain. Global writers/aliases and installed ROM/RAM/IRQ/Flash/OTA are unproved. There is no new BIN or flashability/function-completion claim.

Replay retained objects using the existing LLVM toolchain:

```sh
python3 experiments/tsl9-lookup-mode-rows/verify-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-lookup-mode-rows/build/native-v1
```

For the first compilation use `--trial native-v1`. Output folders are create-only; any existing receipt must match exactly and is never overwritten.
