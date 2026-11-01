# Partial source-object aggregation

[繁體中文](README.md)

Run `python scripts/verify-source-aggregate.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>`. For each of C and C++, the tool freshly compiles 125 existing code units, 13 data units and the 13-byte data window, checks include provenance, and partially links 139 objects. The separate TX candidate package is not included.

The ADC and resident units each export three identically named I/O helpers. The tool verifies that no input imports or relocations reference those names, then localizes the definitions in each object. It retains the input objects and does not edit source.

The unplaced aggregate contains 79 undefined names. Using a hash-pinned historical source object, the tool pairs 71 candidate CODE targets by original address suffix and prelink bytes, plus a 128-byte initializer by contents. It conditionally links 72 aliases and retains seven undefined names. Each alias points to an actual compiled section, rather than a numeric address witness; relocation semantics, original-coordinate layout, overlapping ownership and runtime contracts remain unproved. Including resident and stack-related units does not establish hardware ROM or RAM.

Outputs are `NOT-FLASHABLE-*.o`, not a BIN. The historical object is used as comparison evidence; no firmware is read and no target is executed. Flashability and function are not established.
