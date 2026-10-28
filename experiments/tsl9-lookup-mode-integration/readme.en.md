# Source-curated lookup DATA and original-coordinate integration

[繁體中文](README.md) · [Project](../../readme.en.md) · [C/C++ source](../../src/native/receive/lookup_mode_rows.c)

Three rows totaling48 DATA bytes are now curated into `src/`, the formal manifest and the original-coordinate diagnostic link. Identical C/C++ artifacts match **73,422/76,800 bytes (95.60%)** of the official BIN:69,412 CODE bytes plus4,010 DATA bytes. Byte coverage does not measure feature completion or flash readiness.

|Item|Evidence|
|---|---|
|Sources|160 C/H files;125 CODE units and9 DATA units|
|Comparisons|268 comparisons/536 objects: fully verify the existing532 objects before extension, then compile/check4 origin/curated C11/C++17 DATA objects|
|Retention|All159 previous sources and2,086 frozen parent-proof inputs remain unchanged; only one source and one DATA unit are appended to the manifest|
|Original coordinates|6,182 CODE owners,59 DATA OBJECTs,42 adjacent-only spans;all5,270 typed relocation roles retained|
|Dependencies|Six compiler UND and six existing DATA labels remain;no new provider alias|

The packed state store at `0xD0C8` sets mode byte `0x2000BF39` to2/4/5. A separate `rem 3` update targets phase byte `0x2000BF3A`. Given a completed known store, stable mode, normal entries/valid memory and registers, and a record buffer disjoint from this fixed state, the `0xCF5A` read of `0x1A078 +16*mode+nibble` is limited to mode `{0,2,4,5}` and nibble `0..15`.

|Mode|Original window (exclusive end)|Real DATA owner|
|---|---|---|
|0|`0x1A078..0x1A088`|Final16 bytes of the existing432-byte pool|
|2|`0x1A098..0x1A0A8`|New16-byte row|
|4|`0x1A0B8..0x1A0C8`|New16-byte row|
|5|`0x1A0C8..0x1A0D8`|New16-byte row|

All64 conditionally needed bytes now have real original-coordinate DATA backing. Rows1/3 and other unselected bytes are not filled. No full-table extent or global mode invariant is claimed; the full `1A078` provider remains unresolved. The remaining3,378 bytes contain3,128 deliberately withheld bytes and250 other unselected bytes. No padding or original-BIN copying closes these gaps.

All CODE bytes, owner coordinates and continuation observations are unchanged. The conservative last-instruction scan retains the `0x8034→0x8038` startup/vector-data boundary observation; this work does not prove its physical entry behavior.

[`audit-result-v1.json`](audit-result-v1.json) and [`summary.json`](summary.json) contain actual native/source and independent ELF-reader evidence. The diagnostic `NONLOADABLE-ORIGINAL-LAYOUT.elf` is ET_EXEC with entry0 and zero PT_LOAD segments; **it is not a firmware BIN**. Physical chip identity, installed ROM, RAM/IRQ/Flash/OTA and complete execution remain unproved. No target, HOST model, ISA emulator or hardware is executed.

With retained local build artifacts and the fixed LLVM toolchain, replay without compiling:

```sh
python3 experiments/tsl9-lookup-mode-integration/audit-v1.py --tool-dir "$LLVM_BIN"
```

Build artifacts are outside this text-evidence commit. Missing parent objects must first be rebuilt with their frozen recipes. Equivalent toolchains and other operating systems require separate evidence.

[Feature candidate](../tsl9-lookup-mode-rows/feature-candidates.json): separate mode,phase and provenance conditions in offline diagnostics;not implemented.
