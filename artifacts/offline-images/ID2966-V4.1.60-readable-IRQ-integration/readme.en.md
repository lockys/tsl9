# IRQ integration image: not verified flashable

[繁體中文](README.md)

`NOT-FLASH-VALIDATED-irq-callframe.bin` is an offline source-derived artifact. **It is not verified for the original Bluetooth updater or physical hardware; do not treat it as flashable firmware.**

- Size: 76,800 bytes.
- SHA-256: `47f200dce24be25ac89d57922689da536259935e8615ba8195b10ca192895e1c`.
- Original comparison: ID2966 V4.1.60, SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.
- Readable C/C++ replaces only the IRQ initializer and four RCC helpers. Other original instruction/data carriers are retained; this is not complete recovered source.
- Exactly eight bytes differ at `0x9A44..0x9A4B`, permuting four register-save instructions. Pointwise and asynchronous interrupt equivalence remain unproved.
- Resident ROM is only a numeric `0x40000` address witness, without a ROM implementation. Hardware, runtime, startup, updater acceptance and physical flashing remain incompletely established.

[Sources, rebuild entry points and separate independent reviews](../../../analysis/v4160-irq-image-integration-2026-10-21/readme.en.md). The original APK, 22 vendor BINs and previous source-identical image remain unchanged.
