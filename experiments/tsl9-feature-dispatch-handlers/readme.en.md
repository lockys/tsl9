# Feature-dispatch handler regions

[繁體中文](README.md)

Selected src/handlers.v4.c covers1505C–153BA:862B/339 instructions/93 architectural regions plus32B relative metadata. Its106 relocations comprise88 direct controls,2 PC-relative and16 table bindings. Historical trial field RELA=88 counts direct controls only.

V1 preserves the actual reserved-S0/SP/RA compiler failure. V2 preserves assembler branch expansion and size mismatch. V3 uses explicit typed controls; v4 adds genuine table HI20/LO12 ports.

The preliminary probe has bounded allocation/inventory coverage. Current integration checks are in the [complete dispatch experiment](../tsl9-feature-dispatch/readme.en.md). Raw trials remain unchanged. No target, HOST model, ISA, hardware or network executes.
