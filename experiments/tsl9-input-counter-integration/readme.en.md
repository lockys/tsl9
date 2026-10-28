# Source-curated counter DATA and original-coordinate integration

[繁體中文](README.md) · [Project](../../readme.en.md) · [C/C++ source](../../src/native/receive/input_counter_data.c)

The8-byte readonly window `0x1AB48..0x1AB50` is now in formal `src/`,the manifest and the original-coordinate diagnostic link. Identical C/C++ diagnostic ELFs match **73,430/76,800 bytes (95.61%)** of the official BIN:69,412 CODE bytes plus4,018 DATA bytes. Byte coverage does not measure feature completion or flash readiness.

|Item|Evidence|
|---|---|
|Sources|161 C/H files;125 CODE units and10 DATA units|
|Provenance|270 comparisons/540 objects:retain the parent536-object composite proof,then add4 origin/curated C11/C++17 DATA objects|
|Retention|160 prior sources and2,125 parent-proof inputs;only one source and one DATA unit appended to the manifest|
|Original coordinates|6,182 CODE owners,60 DATA OBJECTs,43 adjacent-only spans;all5,270 typed relocation roles retained|
|Dependencies|Six compiler UND and six existing DATA labels remain;no new provider alias|

The new window contains four halfword read cells. Given a completed known masked store or candidate fill,a counter still in0..3 at the read,and normal entries/stable GP/valid RAM disjoint from caller buffers and the MMIO control word,the `0xA158` read of `0x1AB48+2*counter` needs only these8 bytes.

The original whole CFG has a path bypassing `0xA0FA`;dynamic aliases,SDK/IRQ/DMA effects remain open beyond the two direct writes. Byte width alone still gives a512-byte conservative envelope,including328 bytes outside the provided APP. This does not prove an actual invalid read or full-table declaration size. Eight backed bytes do not establish a global counter invariant,so no full `tsl9_input_state_decoders_static_data_1ab48` provider alias is created.

The candidate slot `0x40048` targets `0x2000039C..0x200003CA`. Besides byte fill,it saves/clears/restores MMIO `0x4002420C` and executes `fence.i`. Clearing `GP+[172,177)` remains conditional on installed-slot identity,valid disjoint RAM/MMIO,normal accesses and no faults/interference. Physical ROM identity and MMIO effects are unproved;see the[archived v2 analysis](../tsl9-input-counter-data/verification-v2.json).

Every previous CODE/DATA owner retains its bytes and coordinates. The new window has alignment4;adjacent existing DATA has alignment1. Keeping both native roles gives43 real spans without changed alignment or padding. CODE and continuation observations are unchanged,including the inherited `0x8034→0x8038` startup/vector-data boundary observation;startup execution is not proved.

[`audit-result-v1.json`](audit-result-v1.json) and [`summary.json`](summary.json) record actual native and independent ELF-reader evidence. The remaining3,370 bytes contain3,128 deliberately withheld bytes and242 other unselected bytes. No padding or original-BIN copying closes those gaps.

The diagnostic ELF is ET_EXEC with entry0 and zero PT_LOAD segments;**it is not a firmware BIN**. Physical chip/ROM/RAM/IRQ/Flash/OTA identity and full execution remain unproved. No target,HOST model,ISA emulator or hardware is executed.

With retained local artifacts and the fixed LLVM toolchain,replay without compiling:

```sh
python3 experiments/tsl9-input-counter-integration/audit-v1.py --tool-dir "$LLVM_BIN"
```

Build artifacts are outside this text commit;missing parent objects must first be rebuilt with their frozen recipes. Composite provenance retains the original532-object proof and subsequent DATA projections;this work does not reparse or compile all540 objects.

[Feature candidate](../tsl9-input-counter-data/feature-candidates.json):offline counter provenance,CFG bypass and ROM side-effect diagnostics;not implemented.
