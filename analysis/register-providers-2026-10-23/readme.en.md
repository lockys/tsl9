# Register providers reconstruction

[繁體中文](README.md) · [C/C++ and verification](../../experiments/tsl9-register-providers/readme.en.md) · [Original frame contracts](frame-contracts.json)

Reconstructed read72B and write76B retain60B/64B of original code outside three SPI calls each. GPIO conditions, argument slots, RA reload and final A0 residue keep their original order, without an added frame or spill.

The two channel conditions must stay independent. Argument slots require fresh32-bit reads after SPI calls; RA must reload before the GPIO cleanup store. `frame-contracts.json` records conditional alias implications, without claiming those aliases occurred on hardware.

The280B partial link contains eight genuine consumer/receiver/read/write FUNCs. Four calls reference internal definitions, eight still need SPI/packet UND providers. All twelve relocations remain. **This is not resolved executable code or flashable firmware.**

Public receipts retain local originals. The public curation record is a path-anonymized derivative bound to the raw original SHA. SPI/packet/resident,full IRQ/main and physical OTA evidence remain open. No RV32/MMIO execution or hardware operation occurred.
