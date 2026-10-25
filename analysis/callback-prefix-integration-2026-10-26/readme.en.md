# Formal integration of fixed-length callback DATA

[繁體中文](README.md)

[Fourteen C/C++ DATA providers](../../src/native/receive/callback_prefix_data.c) are curated: 109 bytes, with every original coordinate and HI/LO reference verified.

| Item | Result |
|---|---|
| Sources | 153 C/H files; 121 code units and 6 independent DATA units |
| C11/C++17 comparisons | 254 comparisons / 508 objects; prior 242 results and 1,453 artifact records unchanged |
| Original-coordinate byte equality | **68,374/76,800 bytes = 89.03%**; CODE 64,544B + DATA 3,830B |
| New DATA | 14 actual positive-size objects / 109 bytes; all six existing zero-allocation DATA labels retained |
| Compiler-undefined providers | 22 to 8; 2 direct entries and 6 DATA-address references |
| Flow | 21,938 instructions, 4,245 direct transfers, 4,861 relocations; zero ordinary sequential-position gaps |

Windows follow original A0 pointer and A2 length arguments. No terminating NUL or original declaration extent is invented. Original calls and branches remain intact; the archived SDK `tmos_memcmp` candidate uses BOOL / TRUE-equal semantics, without substituting standard C `memcmp`. Installed ROM/ABI and actual read contracts remain unproved.

**Compiler UND does not count every runtime gap.** Two still-unprovided candidate callback records point to uncovered CODE at `0x10C36`, `0x10D2E`, `0x10D30`, and `0x11544`. Original pointer values and selected CODE coverage are established; complete callback bodies remain unreconstructed. No handler stubs are supplied.

Resection omits only three unreferenced local markers in non-ALLOC `.comment`: two `$d.1` and one `$d.14`. Every remaining actual symbol role and typed reference is checked.

Byte coverage is not feature completion or flash readiness. The diagnostic ELF has entry 0 and no PT_LOAD. No BIN, target/HOST-model/ISA execution, hardware access, or backend calls. MCU/ROM/RAM/IRQ/BLE OTA compatibility remains unproved.

[Summary](summary.json) · [Evidence](evidence.json) · [Contracts](provider-contracts.json) · [Next steps](next-providers.json) · [Feature proposal](feature-candidates.json)
