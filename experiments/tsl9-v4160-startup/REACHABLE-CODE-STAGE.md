# Reachable code and initialized-data source stage

This stage adds four instruction unions from the original ID2966 V4.1.60
runtime, SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.
The C/C++ translation unit carries original instruction templates and semantic
relocations. It does not infer C-callable prototypes or implement unknown
resident effects.

| Original interval, end exclusive | Bytes | Role established here |
| --- | ---: | --- |
| `10CE0..10D2E` | 78 | Necessary local callee instruction union; following RET/body excluded |
| `11266..11356` | 240 | Necessary callee with final tail to existing11252 code |
| `114E2..11544` | 98 | State updates and opaque nominal40058 tail request |
| `11544..119C8` | 1156 | Bounded17-way relative-table dispatcher and local cases |

All518 admitted instructions are locally CFG-reachable from these selected
entries. The original pointer to11544 is stored at1A678; an original caller
passes the containing1A674 address to opaque nominal401B0. Actual invocation
by that resident is unproved. The selected entries use private NOTYPE0 names,
with no canonical callback or ABI closure. Nineteen indirect calls and one
indirect tail remain opaque.

The17-word table at1A548 remains raw in its existing191-byte RO carrier.
It is checked at original VAs against17 source words/seven genuine instruction
targets; it has zero new table RELA. This preserves a fixed original-address
obligation, rather than pretending the table was made symbolic or duplicating
its storage. Two calls to110F8 reference the existing same-section NOTYPE
anchor11252 with signed addend−346. No new alias or zero-storage provider is
introduced, and the original anchor metadata stays unchanged.

A private2-byte RO OBJECT at1AB44 holds `F1 FF`. Its finite local read is
proved only when live GP+36 retains the initialized pointer; the table has
escaped to an opaque resident. This is a new source view, not proof of an
original complete C object, immutable pointer or resident read extent. The
1AB38/1AB42 pointers and two suggested GATT windows remain unimplemented here.

The full verifier first reruns the unchanged651-allocation gate, then checks
C11/C++17 compile/link results:656 allocations,8267 semantic RELA,72336 code
bytes plus3964 RO bytes, totalling76300 original source bytes. Every inherited
section, symbol occurrence/visibility and8107 semantic RELA remains unchanged.
All23 original named dependencies remain true UND. Strict final linking must
fail; the numeric-address witness is not firmware.

Both modes have14 actual ELF counterexamples covering storage/symbol roles,
extra GLOBAL/ABS providers, control and low relocations, negative addends and
the fixed table. The independently audited numeric witness still has500 source
bytes unrepresented:414 bytes occur as loader padding, with309 source
mismatches, while86 bytes are outside file-backed LOAD. No BIN is exported.

```powershell
python -X utf8 -B experiments/tsl9-v4160-startup/verify-reachable-code-extension.py `
  --current-receipt <absolute-path-to-the-retained-finite-data-verification.json>
```

The original workspace and the delivered project discover their own local
firmware/proof directories. `--firmware` and `--proof-root` select explicit
local inputs. Output is a new compile/link/inspection receipt and ET_REL
partial; no original/rebuilt target execution, emulator, BLE/UART/CAN/Flash,
network access, objcopy output or OTA-ready result is part of this verifier.
