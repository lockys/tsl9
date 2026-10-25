# Integration of original copy-source DATA

[繁體中文](README.md)

Readonly windows `0x19D08..0x19D66` (94 bytes) and `0x19D68..0x19DD2` (106 bytes) are now curated in [src/](../../src/native/receive/record_copy_windows.c). Their bounds follow [82 original instructions and the complete software-copy body](../record-copy-windows-2026-10-25/readme.en.md). The two-byte gap is excluded; physical feature names are not inferred.

## Results

| Item | Verified result |
|---|---|
| C/H files and source units |150 files;121 code units plus3 independent DATA units |
| C11/C++17 original/curated comparison |248 comparisons,496 objects;the prior242 results and1453 artifact records are unchanged |
| New DATA |200 bytes,two actual OBJECTs;no new executable bytes or external dependencies |
| Original-coordinate byte equality |67,655/76,800 bytes=**88.09%**;code64,544B+data3,111B |
| Unresolved providers |29→27;two excluded direct entries plus25 literal DATA-address references |
| Static transfer checks |21,938 instructions,4,245 direct transfers,4,861 relocations;zero ordinary sequential-position gaps |

Both copy-source providers now resolve to real readonly DATA objects. Actual native HI/LO references,call targets and every source byte are checked;prior code and data are retained. Both languages produce the same original-coordinate ELF. It has entry0 and no load segments and remains diagnostic only.

[Summary and limits](summary.json) · [Traceable evidence](evidence.json) · [Provider contracts](provider-contracts.json) · [Next providers](next-providers.json)

## Limits and a useful new check

The static bound argument assumes valid nonwrapping pointers,an available stack and no asynchronous corruption. It does not prove whole-stack safety,original declaration extents or physical effects. Installed MCU/ROM/RAM/IRQ/BLE OTA compatibility remains unproved. No new BIN,firmware execution,HOST model,ISA emulation,hardware access or vendor requests.

[Static completeness checks for these two source providers](feature-candidates.json) are implemented as a basis for a future update-artifact build preflight. They are neither a general OTA compatibility check nor a newly enabled hardware feature.
