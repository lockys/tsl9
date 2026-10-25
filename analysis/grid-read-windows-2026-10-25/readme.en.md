# Grid read windows (experiment)

[繁體中文](README.md)

This page preserves the standalone experiment and its 88.32% baseline. Subsequent [curation and original-coordinate integration](../grid-integration-2026-10-25/readme.en.md) passed; current byte coverage is 88.89%. Physical/OTA compatibility remains unproved.

Capture86 original instructions and audit21,938 selected instructions/64,544 CODE bytes. The first two selected read paths have a conservative **432-byte union**, backed by one actual readonly owner and two zero-allocation DATA labels at offsets0/320.

C11 and C++17 objects match,and two independent ELF readers agree. The experimental ET_REL link preserves all prior CODE/DATA,the four existing DATA labels and4,861 typed relocations;experimental undefined references fall from24 to22.

The third path's `AND7` writes A3;the actual scaled lookup row remains A4. It does not prove a0..7 row bound. Its byte-only syntactic envelope exceeds the image,but this is not proof of an actual runtime out-of-bounds read. The third DATA dependency remains unresolved.

Not yet curated into `src/`,the complete source proof or original-coordinate layout. Accepted coverage remains **88.32% (67,833/76,800 bytes)**. No BIN,target/HOST-model/ISA execution,hardware or backend access. Indirect entries,asynchronous effects,original declarations,physical features and OTA compatibility remain unproved.

[Summary](summary.json) · [Original instructions](evidence.json) · [Read bounds](provider-contracts.json) · [Compiler evidence](native-proof.json) · [Next work](next-providers.json) · [Feature proposal](feature-candidates.json)
