# CH32V208GBU6 hardware candidate

[繁體中文](README.md)

Use the **WCH CH32V208GBU6 (QFN28)** as a specific candidate for subsequent offline analysis, not as a confirmed identification of the original hardware.

User-provided video screenshots identify a CH32V208GBU6 development board in a DIY TSL9 replacement module. They support that replacement design's choice of MCU, but do not show an identifiable chip marking on an original TSL9 or prove identical PCB, pinout, or firmware. The shown CAN, SPI, and MCP2515 pin table applies to the video's design only.

The [official WCH selection table](https://www.wch.cn/products/productsCenter/mcuInterface?categoryId=74) lists the CH32V208GBU6 in QFN28. [Prior original APP analysis](../tsl9-original-APP-library-binding/readme.en.md) found a comparison against the `CH32V20x_BLE_LIB_V1.3` prefix, consistent with this candidate but insufficient to identify the installed ROM or its complete ABI.

The existing [CH32V208/D8W experimental candidate](../tsl9-ch32v208-candidate/README.md) is an older byte-identical V4.1.00 reconstruction and does not integrate all current sources. This record changes no code, pin assignments, or BIN. Six unresolved source dependencies and original-device ROM, startup, memory, IRQ, and OTA compatibility remain unverified.
