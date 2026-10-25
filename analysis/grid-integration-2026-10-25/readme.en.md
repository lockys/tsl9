# Curated grid DATA pool and original-coordinate integration

[繁體中文](README.md)

The [432-byte C/C++ pool](../../src/native/receive/grid_read_windows.c) is curated in `src/`. Two genuine interior DATA labels pass original-coordinate placement and HI/LO reference checks.

| Item | Result |
|---|---|
| Sources | 152 C/H files; 121 code units and 5 independent DATA units |
| Original/curated C11/C++17 comparisons | 252 comparisons, 504 objects; prior 242 results and 1,453 artifact records unchanged |
| Original-coordinate byte equality | **68,265/76,800 bytes = 88.89%**; CODE 64,544B + DATA 3,721B |
| DATA labels | All 4 previous labels retained; 2 added; all 6 backed by actual storage |
| Undefined providers | 24 to 22; 2 direct entries and 20 DATA-address references |
| Flow | 21,938 instructions, 4,245 direct transfers, 4,861 relocations; zero ordinary sequential-position gaps |

The pool spans `0x19ED8..0x1A088`, with zero-allocation labels at offsets 0/320. Its 432 bytes form the conservative union of two selected read windows. No assumed nibble bound of 0..9, original array declaration, or global runtime bound is claimed. The separate `0x1A078` dependency stays unresolved: its `AND 7` modifies A3 while the scaled lookup row remains A4.

Resection omits only two unreferenced local `$d.1` compiler markers in non-ALLOC `.comment`; every remaining actual symbol role and relocation is checked. The old local flow-v2 receipts remain preserved. After fixing their hardcoded summary count, fresh v3 receipts are authoritative.

Byte coverage is not feature completion or flash readiness. The diagnostic ELF has entry 0 and no PT_LOAD. No BIN, target/HOST-model/ISA execution, hardware access or backend calls. Installed MCU/ROM/RAM/IRQ/BLE OTA and private-ABI compatibility remain unproved.

[Summary](summary.json) · [Evidence](evidence.json) · [Contracts](provider-contracts.json) · [Next steps](next-providers.json) · [Feature proposal](feature-candidates.json)
