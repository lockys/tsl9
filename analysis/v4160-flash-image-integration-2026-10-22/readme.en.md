# Complete offline image with eleven readable functions

[繁體中文](README.md)

This milestone integrates the five readable IRQ/RCC functions and six Flash functions into the original complete layout. Actual C11 and C++17 builds each compile 42 units and produce the same 76,800-byte candidate. **This remains an unvalidated offline BIN; safe Bluetooth flashing on the original hardware is not established.**

## Actual reconstruction scope

The 42 units comprise 34 original instruction/data carriers, two IRQ/RCC units and six Flash units. Four carriers remove only the eleven replaced function sections. Readable functions occupy 526 bytes; the remaining code/data largely remains original carriers. This is not complete source recovery.

| Function | Original address | Allocated bytes | Bytes differing from official image |
| --- | --- | --- | --- |
| IRQ initialization | 0x9A42 | 144 | 8 |
| Four RCC helpers | 0x19124 / 0x19142 / 0x19160 / 0x1917E | 120 | 0 |
| Flash quarter wrapper | 0x9C0A | 64 | 6 |
| Flash status | 0x18E90 | 8 | 0 |
| Flash unlock | 0x18E98 | 30 | 12 |
| Flash lock | 0x18EB6 | 14 | 0 |
| Flash erase | 0x18EC4 | 46 | 21 |
| Flash 64-word program | 0x18EF2 | 100 | 23 |

Complete image SHA-256: `de159bb345b27250a683e197dd84b04e51a7a7ed89315347395baaea53f68be1`. It differs from the official image in 70 bytes: eight prior IRQ save-order bytes and 62 Flash component bytes. The official and previous candidate files are preserved.

## Evidence and checks

All 691 allocations remain. The 680 retained original storage sections and 53 section-relative bindings are checked separately. The new object contains 8,270 actual RELA records: 8,259 outside records retain full roles and multiplicity, plus eleven readable-function JALs. Relative to the original 8,280 records, four IRQ helper and six Flash private branch records are explicitly discharged through actual bytes, PCs, conditions and destinations, without fake private labels or numeric ABS providers.

All twenty incoming entry references are checked, including two compressed C.JAL calls with `PC+2` return addresses and a tail jump that writes no new RA. Raw partial-object storage and linked image bytes are compared at their respective layers.

Strict linking still rejects the missing ROM provider. Successful linking uses only a numeric `0x40000` address witness and supplies no ROM bytes. Every exported byte must be supported by actual sections and LOADs; no holes, NOP padding, original-BIN fallback, RAM NOBITS or ROM bytes are exported.

Each language checks 56 actual compiler/link/export commands, 42 dependency rules associated with their exact source and adapter, and 194 actual artifact hashes. Twenty-three ELF/relocation/image controls and three actual dependency-file controls are rejected; the independent ABI review adds twenty actual-artifact mutations per language. These are offline checker results, not physical-device tests.

- [Implementation and actual build evidence](implementation/readme.en.md)
- [Independent source, layout and image review](source-review/readme.en.md)
- [Independent ABI and branch review](ABI-review/readme.en.md)
- [Bounded literal interior-reference inventory](numeric-interior/readme.en.md)

The supplemental inventory examines 1,030 interior literal values at every byte offset of each of three exact images, with no hits and ten synthetic detector controls. It does not rule out ROM, computed or separately encoded references.

## Portable entry and limitations

From the project root run `python experiments/tsl9-v4160-flash-image-integration/verify.py --tool-dir <LLVM-bin> --language both`, or use sibling `verify.sh`. Only host LLVM compiler/linker tools execute; RV32 objects and images are inspected as data. Windows Python/LLVM evidence does not establish shell, Linux, macOS or CI execution.

Original Flash program boundary `+8`, scratch registers, fault/nonreturn GPR prefixes, pointwise IRQ save state and asynchronous equivalence remain unproved. Original board/chip, ROM, Flash, installed BOOT and BLE OTA compatibility also remain unverified. WCH CH32V20x/208 remains a hardware candidate; successful compilation does not identify the chip.

Worthwhile future features include local update-file preflight and portable offline evidence export: check provenance, hashes, roles and version evidence before hardware action, and produce a replayable report. These remain proposals and are not new original-device functions.
