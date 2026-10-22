# Experimental OTA C-wired BIN — NOT FLASH VALIDATED

[繁體中文](README.md)

`NOT-FLASH-VALIDATED-ota-source-wired.bin` is an offline compile/link artifact, **not firmware validated for the original BLE OTA hardware**. Actual C11/C++17 outputs have identical bytes.

| Field | Value |
|---|---|
| Size | 77,824 bytes /76 pages of1,024 bytes |
| SHA-256 | `3be918942c03de99c8a5f3fb7d6eba40ab9af63930020efb7f4cac07cc9a10ee` |
| Inherited TX-integrated image | 76,800 bytes, SHA-256 `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89` |
| Original caller | JAL at `0x14094` reaches real C at `0x1AC00`, RA `0x14098` |
| Differences in inherited range | Three bytes, all in that caller instruction |
| Appended extent | Executable C568 and explicit non-executable FF456 page data |

The old530-byte handler remains; extensive original carriers remain. This is not a complete readable-source rewrite. The partial link retains a true ROM undefined symbol. The complete ELF uses only the historical numerical `0x40000` address witness, corroborated by the original instruction, without supplying a ROM implementation.

Flash/NV ownership, physical ROM/BOOT/RAM, interrupt/callee/stack ABI, OTA acceptance and failure recovery remain unproved. No RV32, BLE/UART/CAN or Flash execution occurs. This artifact does not establish flashing compatibility.

[Source and static evidence](../../../analysis/v4160-ota-source-wiring-2026-10-22/readme.en.md) | [Readable model](../../../experiments/tsl9-v4160-ota-source-wiring/readme.en.md)
