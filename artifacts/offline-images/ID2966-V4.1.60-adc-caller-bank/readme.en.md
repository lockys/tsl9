# ADC caller candidate without flash validation

[繁體中文](README.md)

`NOT-FLASH-VALIDATED-adc-caller-bank.bin`:78848bytes, SHA256 `ecd2a9fe757117ab8af19211a56c5090dc3a2c777422fcd12ca2fb6298565e55`.

The old77824-byte experimental image remains separate. Only its copied19896 caller is wired by a real JAL to the110-byte C/C++ function at1B000, retaining RA1989A. An appended page includes914bytes of explicit FF packaging data. The old88-byte function remains;110bytes are not squeezed into its extent.

Only a conditional normal caller projection passes. Private-frame residue, full callee ABI, fault/asynchronous/IRQ behavior, Flash/NV ownership, installed ROM, BOOT and physical BLE OTA remain unproved. Raw BIN encodes no execute permissions. Compilation/link/synthetic evidence does not establish flashability; no hardware was accessed.

The candidate inherits the older568-byte OTA component and ROM address-witness limits. [Integration sources and actual verification](../../../analysis/v4160-adc-caller-2026-10-22/integration/readme.en.md); [complete milestone evidence](../../../analysis/v4160-adc-caller-2026-10-22/readme.en.md).
