# Source-curated sequence DATA and original-coordinate integration

[繁體中文](README.md) · [Project](../../readme.en.md) · [C/C++ source](../../src/native/receive/sequence_pattern_data.c)

The48-byte readonly window `0x1A638..0x1A668` now belongs to formal `src/`,the manifest and the original-coordinate diagnostic link. Identical C11/C++17 diagnostics match **73,478/76,800 bytes（95.67%）**:69,412B CODE plus4,066B DATA. This measures static bytes,not feature completion or flash readiness.

|Item|Verified evidence|
|---|---|
|Sources|162 C/H files;125 CODE and11 DATA units;272 comparisons/544 objects in a composite proof|
|Retention|161 prior sources,parent540-object proof and2,164 parent inputs;four new origin/curated C11/C++17 DATA objects|
|Coordinates|6,182 CODE owners,61 DATA OBJECTs,43 adjacent spans;all5,270 relocation roles retained|
|Dependencies|Six compiler UND and six existing DATA labels retained;no new full-provider alias|

Under the[whole callback/candidate comparator contracts](../tsl9-sequence-pattern-data/readme.en.md),the six-byte read at `0x12046..0x1205E` uses `0x1A638+6*(2*channel+state)`. Channel is0..3;the48B suffices only while each state read is0/1,inputs are valid/nonnull,GP/saved registers remain stable,and candidate slot/Xwchc/MMIO/disjointness/no-interference conditions hold.

For valid nonnull input,the candidate returns1 for equality and0 for a different byte;null/zero length also returns1. Preserve this Boolean convention instead of standard C `memcmp`. The conditional two-stage interpretation is state0→1,then1→2→0 and low-byte marker `0x80+channel`. Physical buttons or vehicle actions remain unidentified.

Global state bounds and installed ROM identity remain unproved;the opaque `tsl9_registered_callbacks_static_data_1a638` provider is not bound. The byte-state envelope remains1,572B,including92B outside the supplied APP. It proves neither a real invalid read nor full declaration extent. Only48B were selected;no withheld payload or individual hash was emitted.

Every prior owner byte/coordinate and CODE continuation observation remains,including the inherited `0x8034→0x8038` startup/vector boundary. The3,322 remaining bytes comprise3,128 deliberately withheld and194 otherwise unselected bytes;no padding or copied original image fills the gaps.

[`audit-result-v1.json`](audit-result-v1.json) and[`summary.json`](summary.json) retain actual native and independent-reader evidence. ET_EXEC/entry0/noPT_LOAD diagnostics are **not firmware BINs**. Original ROM/RAM/IRQ/Flash/OTA,execution and flash compatibility remain unproved. No target,HOST model,ISA emulator or hardware execution occurred.

With frozen local parent objects and LLVM,read-only replay is:

```sh
python3 experiments/tsl9-sequence-pattern-integration/audit-v1.py --tool-dir "$LLVM_BIN"
```

Only text sources/evidence are committed;this round does not reparse or compile all544 objects. The[feature candidate](../tsl9-sequence-pattern-data/feature-candidates.json)is an unimplemented offline sequence-state diagnostic.
