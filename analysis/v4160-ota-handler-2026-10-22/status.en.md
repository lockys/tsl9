# Current scope and gaps toward a native-device BIN

[繁體中文](status.zh-TW.md)

The complete-image baseline is the experimental TX image retained at GitHub `fd48bf5`, SHA-256 `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`. This milestone's separate OTA handler is described in this directory. Bytes from an unintegrated object must not be counted in the complete BIN.

## Actual source coverage

The 76,800-byte image has thirteen original function regions / 930 bytes supplied by readable C/C++ and explicit ABI stages: eight bytes are a standard assembly entry; 922 bytes come from C/C++ units including small primitives and explicit ordering. The other 75,870 bytes retain original carriers: 71,526 bytes executable storage and 4,344 bytes nonexecutable storage. An additional 35,160-byte NOBITS RAM allocation is absent from the BIN.

These are byte/storage-source counts, **not feature completion percentages**. Original opcodes embedded in C compilation units do not become readable C reconstruction. The unintegrated 624-byte callback is excluded from 930.

The actual `source-integrated.o` has 691 nonempty allocations and one true UND, `__tsl9v4160_rom_entry`. The historical count of 31 unresolved symbols is not current ELF state. Later real storage and relative labels resolved location obligations without proving resident, callback, lifetime or physical ABI contracts.

Evidence is the [complete TX integration](../v4160-tx-image-integration-2026-10-22/readme.en.md) and its local `build/formal-v1/c/verification.json` (SHA-256 `9b76a657fae241ab83a598ced274bbd819ffd45dc1c5133d33281f00311bb2e7`). The reread `source-integrated.o` SHA-256 is `85c674487c0bf2b0bbcbc3f0f5607d82dd07014acaf0634cfd45525ccdcdf456`.

## Evidence still required

| Requirement | Available scope | Necessary missing evidence |
| --- | --- | --- |
| App program | Partial readable C/C++, original carriers, reproducible synthetic HOST and native compilation evidence | More typed native control/update paths, real provider binding and complete layout. |
| MCU/ISA/board | WCH CH32V208/D8W candidates, numeric peripheral settings and SDK associations | Independent physical MCU/instruction profile and board/component/wiring identity. |
| ROM | Two official candidates, some closed small functions and the app's expected-version-prefix comparison | Installed resident identity and necessary interface/call contracts. Depending on onboard ROM does not require reconstructing the entire ROM merely to remove UND. |
| RAM/startup/IRQ | Original startup/GP/SP/RAM/IRQ evidence and partial C implementations | Actual memory availability, aliases, initialization/visibility, interrupt entry/exit and asynchronous observation. |
| BOOT/Flash | Candidate BOOTs, numeric writes, page shapes and byte anchors | Installed BOOT identity, physical Flash rules and BOOT/Runtime transition. Shapes and anchors alone do not prove compatibility. |
| BLE OTA/recovery | Static APK/BIN format, reply/retry chains; user reports App updating official BINs | Actual rebuilt-image acceptance, CRC/signature rules, failure and recovery. Official-image success does not prove rebuilt-image success. |

## Sufficient conservative checks are not the only possible implementation

530/632 bytes describe original storage, not the exact size every correct C implementation must emit. Required evidence concerns semantics, live ingress/continuations, observable ABI and complete layout provenance. A shorter function does not turn remaining executable bytes into padding. A larger function cannot overwrite adjacent regions or borrow original code as fallback.

RA must return correctly and preserve observable semantics; its number need not always be identical. The closed candidate `+0x13C` evidence conditionally narrows only that slot, not other callees or installed ROM. Byte/RA equality may be sufficient conservative evidence, but must not replace interface/behavior analysis or become an unsupported admission exemption.

This milestone increases real App C/C++ by implementing the U/S/W/R/E body at `0x9C4A..0x9E5C`, connecting four Flash primitives, readback, scheduling and replies. Its W path writes BOOT, so it alone cannot prove new Runtime flashing. The full goal remains open. Offline packet preflight and wait-reason displays remain proposals, not verified hardware features.
