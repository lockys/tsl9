# Complete offline image with original register/save order

[繁體中文](README.md)

`NOT-FLASH-VALIDATED-register-scheduled.bin` contains 76,800 bytes with SHA-256:

```text
0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667
```

It is byte-identical to archived official ID2966 V4.1.60. Separate C11/C++17 pipelines freshly compile 42 translation units, explicitly schedule ABI saves, link and export. Eleven readable functions account for 526 bytes; remaining contents are original carriers. This is partial source recovery. Compiler-only and scheduled objects are preserved separately and must not be conflated.

Generation does not fill holes or replace functions from an original BIN and supplies no ROM bytes. The original BIN is a comparison reference; existing carriers are identity-bound C files and relocation declarations. See the [integration guide](../../../analysis/v4160-register-image-integration-2026-10-22/readme.en.md) and [standalone scheduling tool](../../../experiments/tsl9-v4160-frame-schedule/readme.en.md).

**Not verified as flashable.** Resident ROM, installed BOOT, exact chip/board, physical interrupts/Flash, BLE update acceptance and recovery remain unconfirmed. This artifact is not a flashing recommendation. No RV32 execution/emulation or physical device access occurred.
