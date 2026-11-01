# Partial source-object aggregation

[繁體中文](README.md)

Run `python scripts/verify-source-aggregate.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>`. For each of C and C++, the tool freshly compiles 125 existing code units, 13 data units and the 13-byte data window, checks include provenance, and partially links 139 objects. The separate TX candidate package is not included.

With `--tx-candidate <CANDIDATE_BIN>`, it freshly compiles candidate TX, verifies its 280-byte window and replaces the old transport unit with a composite of its three ordered sections. The eight visible references from other objects all target the old entry, which receives a candidate alias to the new entry. This is an unplaced partial link; indirect interior entries and runtime ABI remain unproved. The mode retains the additional TX RAM import, for eight unresolved names.

The ADC and resident units each export three identically named I/O helpers. The tool verifies that no input imports or relocations reference those names, then localizes the definitions in each object. It retains the input objects and does not edit source.

The unplaced aggregate contains 79 undefined names. Using a hash-pinned historical source object, the tool pairs 71 candidate CODE targets by original address suffix and prelink bytes, plus a 128-byte initializer by contents. It conditionally links 72 aliases and retains seven undefined names. Each alias points to an actual compiled section, rather than a numeric address witness; relocation semantics, original-coordinate layout, overlapping ownership and runtime contracts remain unproved. Including resident and stack-related units does not establish hardware ROM or RAM.

Outputs are `NOT-FLASHABLE-*.o`, not a BIN. The historical object is used as comparison evidence; no firmware is read and no target is executed. Flashability and function are not established.

## Original-coordinate diagnostic link

`python scripts/verify-source-layout.py --tool-dir <LLVM_BIN> --candidate <CANDIDATE_BIN> --out <NEW_OUTPUT_DIR>` rebuilds the TX source aggregate and comparison layout, then places source sections using symbols and prelink bytes from the historical source object. For each of C and C++, 6,235 nonoverlapping sections totaling 73,551 bytes match the existing candidate diagnostic layout after relocation; the excluded ranges are skipped.

The strict link must report seven unresolved names: the six APP dependencies and the TX RAM dependency. For selected-section comparison only, the diagnostic link uses numerical witnesses for those names; these are not actual code or data providers. Its ELF has zero `PT_LOAD`, is not flashable, and does not contain all 76,800 bytes or establish missing data, startup, ROM/RAM or hardware behavior. The workflow still depends on a historical source object and the TX postpass, so it is not a standalone `src/` build.
