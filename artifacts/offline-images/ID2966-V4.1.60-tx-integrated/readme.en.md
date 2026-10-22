# Experimental TX image: not verified as flashable

[繁體中文](README.md)

`NOT-FLASH-VALIDATED-tx-integrated.bin` is the identical complete experimental image produced by fresh C11 and C++17 pipelines. It is not an official download and has not been validated on physical hardware or BLE OTA.

- Size: 76,800 bytes.
- SHA-256: `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`.
- Official reference: ID2966 V4.1.60, SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.
- Exactly 93 differing bytes, all within TX `0x8A56..0x8B6E`; all other bytes are identical.
- Thirteen original function regions / 930 bytes use fifteen allocated FUNC roles; 678 other sections retain original carriers. This is partial source reconstruction.

The file is copied from the matching formal producer outputs without overwriting the 22 official BINs. [Source and independent review](../../../analysis/v4160-tx-image-integration-2026-10-22/readme.en.md) cover actual source, allocation, relocation, calls and page shape. ROM/BOOT identity, physical Flash aliasing, full ABI, CRC/signature policy, OTA and failure recovery remain unproved. This artifact is for offline research and carries no flashing-readiness claim.
