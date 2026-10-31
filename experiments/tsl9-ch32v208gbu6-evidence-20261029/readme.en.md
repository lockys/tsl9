# CH32V208GBU6 hardware candidate

[繁體中文](README.md)

A user-provided close-up of the original TSL9 board shows the main chip marked **CH32V208** and **GBU6**. This is direct marking evidence for the photographed board; use **WCH CH32V208GBU6 (QFN28)** for subsequent offline analysis. The photograph does not establish the chip internals, other revisions, PCB wiring, resident ROM or firmware compatibility.

Earlier user-provided video screenshots identify a CH32V208GBU6 development board in a DIY TSL9 replacement module. The newer original-board close-up independently supplies chip-marking evidence. The video's CAN, SPI, and MCP2515 pin table applies to that DIY design only.

The [official WCH selection table](https://www.wch.cn/products/productsCenter/mcuInterface?categoryId=74) lists the CH32V208GBU6 in QFN28. [Prior original APP analysis](../tsl9-original-APP-library-binding/readme.en.md) found a comparison against the `CH32V20x_BLE_LIB_V1.3` prefix, consistent with this candidate but insufficient to identify the installed ROM or its complete ABI.

The existing [CH32V208/D8W experimental candidate](../tsl9-ch32v208-candidate/README.md) is an older byte-identical V4.1.00 reconstruction and does not integrate all current sources. This record changes no code, pin assignments, or BIN. Six unresolved source dependencies and original-device ROM, startup, memory, IRQ, and OTA compatibility remain unverified.

## Static memory configuration comparison

The [WCH evaluation document](https://www.wch.cn/uploads/file/20220627/1656323204206699.pdf) lists CH32V208x example Flash/RAM allocations of 128/64, 144/48 and 160/32 KiB at Flash base `0x00000000` and RAM base `0x20000000`. Under that contiguous mapping and without remapping the APP addresses, the [reset audit](../tsl9-reset-state-bootstrap-contract/readme.en.md) records a zeroing interval `[0x20004080,0x2000C958)` extending 2,392 bytes beyond the 48 KiB RAM end; the verified [clock frame](../tsl9-clock-reset-noninterference/readme.en.md) also uses `[0x2000FFF0,0x20010000)`. Both fit only the 64 KiB RAM example among the three. This does not read the device configuration or exclude alternative mappings.

The assumed APP interval `[0x8000,0x1AC00)` is 76,800 bytes and numerically fits each example Flash range. That does not establish write permissions, BOOT/ROM occupancy, OTA compatibility or successful execution. Official documents differ in their descriptions of total and zero-wait Flash; no physical configuration is inferred from addition alone.

## Conditional CAN pin comparison

The 34 bytes at `0x12DC0..0x12DE2` in the original ID2966 V4.1.60 APP match the same addresses in the current C reconstruction diagnostic ELF. The whole APP SHA-256 is `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`. Calls at `0x12DCC` and `0x12DDE` respectively receive `(0x40010800, 0x1000, 0x18)` and `(0x40010800, 0x0800, 0x48)`. Under the [WCH peripheral definitions](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32v20x.h) and [GPIO mode definitions](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32v20x_gpio.h), these correspond to GPIOA pin 12 with alternate-function push-pull and pin 11 with pull-up input. This interpretation is conditional on helper `0x9A24` implementing the corresponding parameter contract.

The [WCH CH32V208 datasheet](https://atta.szlcsc.com/upload/public/pdf/source/20240411/5E05523CBB231C22A5C78C078317BD2C.pdf) lists QFN28 PA12/pin 19 as CAN1_TX and PA11/pin 18 as CAN1_RX, matching the user-provided DIY reference. Agreement among the chip definitions, call arguments and DIY pin table does not prove the original board wiring, remapping, transceiver or CAN frame behavior; it is not sufficient evidence to flash.

### GPIO helper instruction evidence

A further comparison against the original V4.1.60 APP finds exact matches in the current C diagnostic ELF for `0x9A24..0x9A42` (30 bytes) and `0x18F88..0x1904A` (194 bytes). The `0x9A24` helper stores the low 16 bits of a1 as the pin mask, places 3 at the configuration structure's speed field and stores a2 as mode before calling `0x18F88`. The latter takes the low mode nibble, combines speed for output modes, and updates GPIO configuration fields using the mask; mode `0x48` on the high-pin path additionally writes the selected bit to `base+0x10`. This data flow agrees with the WCH GPIO structure and mode definitions, narrowing the helper contract uncertainty above.

This is a static comparison of original instructions with the candidate SDK, conditional on a valid stack, normal calls and the candidate memory mapping. No actual register values, physical wiring or vehicle function have been tested.

### Controller initialization and diagnostic candidate

The original V4.1.60 ranges `0x18AB0..0x18BA2` (242 bytes) and `0x12E2A..0x12E4C` (34 bytes) both match the current C diagnostic ELF at the same addresses. The call at `0x12E34` passes `0x40006400` as its first argument; that is the WCH CAN1 base. The initializer clears control bit 1, sets control bit 0, polls status bit 0 and returns a status. This is consistent with the initialization entry, exit and status checks in [WCH CAN initialization](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/src/ch32v20x_can.c), without claiming the two functions are fully equivalent.

After the call returns, `0x12E38..0x12E4C` does not check the a0 return value before reading `0x40006414`, ORing 2 and writing it back, then returning. Reporting the initializer return state is a possible future read-only diagnostic; it is not implemented. Static instructions do not prove initialization failure, actual register values or safe access to the device.

## Original-board photographs and SPI protocol

User-provided photographs of the original board show `TSL9`, three labeled CAN H/L pairs, and at least one chip legibly marked `MCP2515`; a second similar chip's complete marking is not confirmed. A newer close-up shows the main chip marked `CH32V208` and `GBU6`. Photographs are not included in the public repository. These observations do not measure electrical connections.

The 254 bytes of V4.1.60 at `[0x16896,0x16994)` match the current C diagnostic ELF at the same addresses. The existing [SPI reconstruction](../tsl9-spi-write-providers/readme.en.md) records that `0x168DE` passes `0x02` followed by an address to the transfer helper, while `0x1693E` passes `0x05`, address, mask and value. This matches the WRITE and BIT MODIFY command formats in the [Microchip MCP2515 datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/MCP2515-Stand-Alone-CAN-Controller-with-SPI-20001801J.pdf), supporting a possible relationship between the pictured component and the analyzed path. Matching a common protocol does not prove physical routing or successful transmission.

The observed selector bits respectively write `0x10` and `0x01` to `0x40010814`; under the WCH GPIOA mapping these select PA4 and PA0, consistent with the two candidate CS pins in the DIY design. The original PCB routing, identity of the second controller and pin assignments remain unverified; this evidence does not establish flashability.
