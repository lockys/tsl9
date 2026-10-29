# CH32V208GBU6 hardware candidate

[繁體中文](README.md)

Use the **WCH CH32V208GBU6 (QFN28)** as a specific candidate for subsequent offline analysis, not as a confirmed identification of the original hardware.

User-provided video screenshots identify a CH32V208GBU6 development board in a DIY TSL9 replacement module. They support that replacement design's choice of MCU, but do not show an identifiable chip marking on an original TSL9 or prove identical PCB, pinout, or firmware. The shown CAN, SPI, and MCP2515 pin table applies to the video's design only.

The [official WCH selection table](https://www.wch.cn/products/productsCenter/mcuInterface?categoryId=74) lists the CH32V208GBU6 in QFN28. [Prior original APP analysis](../tsl9-original-APP-library-binding/readme.en.md) found a comparison against the `CH32V20x_BLE_LIB_V1.3` prefix, consistent with this candidate but insufficient to identify the installed ROM or its complete ABI.

The existing [CH32V208/D8W experimental candidate](../tsl9-ch32v208-candidate/README.md) is an older byte-identical V4.1.00 reconstruction and does not integrate all current sources. This record changes no code, pin assignments, or BIN. Six unresolved source dependencies and original-device ROM, startup, memory, IRQ, and OTA compatibility remain unverified.

## Static memory configuration comparison

The [WCH evaluation document](https://www.wch.cn/uploads/file/20220627/1656323204206699.pdf) lists CH32V208x example Flash/RAM allocations of 128/64, 144/48 and 160/32 KiB at Flash base `0x00000000` and RAM base `0x20000000`. Under that contiguous mapping and without remapping the APP addresses, the [reset audit](../tsl9-reset-state-bootstrap-contract/readme.en.md) records a zeroing interval `[0x20004080,0x2000C958)` extending 2,392 bytes beyond the 48 KiB RAM end; the verified [clock frame](../tsl9-clock-reset-noninterference/readme.en.md) also uses `[0x2000FFF0,0x20010000)`. Both fit only the 64 KiB RAM example among the three. This does not read the device configuration or exclude alternative mappings.

The assumed APP interval `[0x8000,0x1AC00)` is 76,800 bytes and numerically fits each example Flash range. That does not establish write permissions, BOOT/ROM occupancy, OTA compatibility or successful execution. Official documents differ in their descriptions of total and zero-wait Flash; no physical configuration is inferred from addition alone.

## Conditional CAN pin comparison

The 34 bytes at `0x12DC0..0x12DE2` in the original ID2966 V4.1.60 APP match the same addresses in the current C reconstruction diagnostic ELF. The whole APP SHA-256 is `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`. Calls at `0x12DCC` and `0x12DDE` respectively receive `(0x40010800, 0x1000, 0x18)` and `(0x40010800, 0x0800, 0x48)`. Under the [WCH peripheral definitions](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32v20x.h) and [GPIO mode definitions](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32v20x_gpio.h), these correspond to GPIOA pin 12 with alternate-function push-pull and pin 11 with pull-up input. This interpretation is conditional on helper `0x9A24` implementing the corresponding parameter contract.

The [WCH CH32V208 datasheet](https://atta.szlcsc.com/upload/public/pdf/source/20240411/5E05523CBB231C22A5C78C078317BD2C.pdf) lists QFN28 PA12/pin 19 as CAN1_TX and PA11/pin 18 as CAN1_RX, matching the user-provided DIY reference. Agreement among the chip definitions, call arguments and DIY pin table does not prove the original board wiring, remapping, transceiver or CAN frame behavior; it is not sufficient evidence to flash.
