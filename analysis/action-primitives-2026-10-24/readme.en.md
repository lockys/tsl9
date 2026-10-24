# Action primitives and cyclic output: static C/C++

[繁體中文](README.md)

Nine complete functions add684B /231 instructions and a24B relative table to [action_primitives.c](../../src/native/receive/action_primitives.c). C11/C++17 checks cover every original code/table byte and62 relocations. [Raw evidence](evidence.json) · [Address contracts](provider-contracts.json).

- **Confirmed:**1552A sets pending byte358,which the prior155D0 consumer clears before18110. 15532 writes config bit8 from the input low bit,but later branches/tail arguments retain the full input; it is not reduced to a boolean.
- **Confirmed:**1802E merges or replaces the full mask;17F80 mirrors it,calls17C4E and then reloads mask/counter fields.1805A uses a six-entry table/four targets and reloads the phase byte after output before REM6. [Phase constants](phase-map.json).
- **Confirmed:**1811A retains the original flag update,conditional delay arguments,and start/cancel paths. Values2/20/100/200/300/8000 are numeric observations; time units and scheduler mode remain unproved.
- **Unknown:** product feature names,including a DND label for bit8. Six old imports resolve,two new dependencies17C4E/9AE4 emerge,and181 genuine imports remain. [Inventory](next-providers.json).

Complete source proof covers122 C/H files,192 comparisons /384 objects;prior121 C/H files and1129 artifact records remain unchanged. Legacy V4.1.00 reference tests were not rerun. The native component has31,468B code +1,750B data /2,069 relocations. All33,218 selected bytes match original nominal coordinates in a diagnostic ELF with **no PT_LOAD**,entry0. Static flow checks cover11,050 instructions,1,853 direct transfers and669 call-return positions with no ordinary continuation gaps. Both the retained253-entry action table and new six-entry phase table are checked against actual linked data; runtime targets,488 indirect transfers,10 MRET and trap resumption remain unproved. [Summary](summary.json).

[Feature candidates](feature-candidates.json) describe read-only output diagnostics and numeric phase inventory. They do not claim a working hardware feature. No target/host/ISA execution,hardware,BLE/CAN/Flash or vendor network access;no BIN generated. MCU,installed ROM,full startup/RAM/IRQ and OTA compatibility remain unproved.
