# Callback, packet checksum and state paths

[繁體中文](README.md)

The same [C source](src/callback.v4.c) was compiled as C11 and C++17: seven original spans, 314 bytes, 109 instructions and 31 architectural regions. Data-only relocation encoding at recorded original addresses matches every byte against official ID2966 V4.1.60. There are 20 direct-control and six PC-relative relocations. This is neither a normal C ABI implementation nor flashable firmware.

828C reads the live counter at 2000BFB4. ED00 adds header and length-delimited payload bytes while excluding the A1 index. 1069E selects index7 and compares against a fresh byte at then-live S0+10. 106E8 performs a separate counter read/increment after its guard. 1074C/107C0 update state and register deferred work. 1083C invokes A5 at10846, then conditionally clears state and registers107C0. Called implementations remain explicit unresolved dependencies.

C owns arithmetic, constants and ordinary memory. SP/RA/S0, control and PC effects are architectural ports. v1/v2 compiled but failed exact comparison because LLVM commuted the ED24 ADD operands. v3 changes the empty input-port declaration order while retaining C arithmetic and emits the original encoding. Failed trials remain unchanged; matching was not relaxed.

```sh
python3 experiments/tsl9-feature-callback/build-v4.py --tool-dir "$LLVM_BIN" --trial YOUR_NEW_TRIAL
python3 experiments/tsl9-feature-callback/build-v4.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-feature-callback/build/trial-v4
```

Existing LLVM and the official BIN are required; nothing is downloaded. Replay requires retained local originals. No hardware, network, HOST model, ISA or target execution and no new malformed-input/negative matrix. Bounds, concurrency, IRQ, memory ownership, resident ROM, scheduler9124 and external callbacks remain unproved.

Potential additions: read-only checksum rejection counts, callback rejection reasons and pending-work diagnostics. These are proposals, not implemented or hardware-verified features.

## Genuine integration

v4 binds both clear calls to the existing strong `tsl9_queue_external_820c` definition; it does not add a duplicate helper or an ABS substitute. Both languages genuinely link 5402 code bytes and60 table bytes,432 FUNC,412 RELA. Three parent direct dependencies now have true definitions. The expanded graph exposes75 unresolved symbols (73 direct and2 literal-code references), plus resident/indirect obligations; this is not a complete firmware graph.

```sh
python3 experiments/tsl9-feature-callback/integrate-v2.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-feature-callback/build/graph-v2
```

98 source comparisons /196 objects pass; the prior96 results and577 artifact records are unchanged. Parent validation proves an exact one-file/one-unit manifest extension. It does not replay the old whole-manifest receipt under changed metadata. Standalone and curated ELF carriers have different local FILE names; code, relocation carriers and all other parsed symbols match, and both actual hashes are pinned. ET_REL VMAs remain0, so this graph cannot be executed or flashed.
