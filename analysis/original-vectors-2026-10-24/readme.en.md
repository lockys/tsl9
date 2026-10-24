# Original vector data and startup component

[繁體中文](README.md) · [Results](summary.json) · [C/C++ source](../../src/native/startup/boot_vectors.c)

A genuine C function-address array preserves328B from8038–8180:62 nonzero address words,20 zero words and61 distinct entries. **82 words are not a confirmed hardware IRQ count.** Trailing zeros are preserved; complete hardware vector extent remains unproved.

C11/C++17 emit62 R_RISCV_32 references. Every slot, type, addend and target is checked; all328B match after data-only relocation encoding. Unresolved entries are not replaced by fixed integers or fake functions.

| Genuine partial link | Result |
| --- | --- |
| Code/data | Original572B/212 instructions and128B initializer unchanged;328B vector data added |
| References | 144 RELA;55 pointer slots bind genuine rebuilt entries;7 slots reference6 external entries |
| Outstanding | 8448,8498,979E,12C24,16FB6,19BD4 plus main9008 and resident40000:8 UND |
| Product | Identical C/C++ products; VMA0 ET_REL, not a flashable BIN |

The manifest explicitly registers native_data_units. The frozen function verifier is unchanged:53 code units pass106 comparisons/212 objects, preserving all prior106 results and637 artifact records. Independent pointer data adds2 source comparisons/4 objects, giving108 comparisons/216 objects across the current verification scopes. The source inventory contains80 C/H files; legacy references are not thereby established as native firmware.

The [provenance index](publication-provenance.json) binds3 portable original receipts and1 reversible path-only derivative of the data compilation receipt. Raw receipts remain local. The [six bounded entry prefixes](entry-frontier.json) select at most64B each and may continue past RET/MRET into adjacent code; they are not complete-procedure or IRQ-compatibility proofs.

Offline vector coverage reporting is now implemented as verification tooling. Device boot/IRQ health diagnostics remain a candidate requiring IRQ-context, state-ownership and protocol proof.

MCU/ROM identity, complete IRQ context, memory ownership, main closure, final placement, actual boot and BLE OTA remain unverified. No target/HOST execution, ISA emulation, hardware/network operation or BIN generation occurred. Commit/push remain held for historical personal information.

See [experiment and replay](../../experiments/tsl9-original-vectors/readme.en.md).
