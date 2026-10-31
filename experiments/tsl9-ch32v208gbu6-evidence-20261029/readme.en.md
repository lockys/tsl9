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

Original `0x1706C/0x170B8` forms `s0=0x40010800`, then `0x17132..0x17168` calls `0x9A24` five times using that base. Under the existing helper contract, [WCH GPIO mode definitions](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32v20x_gpio.h), preserved registers/stack, valid mapping and normal initialization, these operands request:

| GPIOA pin | Mode operand | Candidate WCH interpretation |
| --- | --- | --- |
| PA4, PA0 | `0x10` | General push-pull output |
| PA5, PA7 | `0x18` | Alternate-function push-pull output |
| PA6 | `0x48` | Pull-up input |

The same path then initializes and enables the SPI candidate at numeric base `0x40013000` at `0x1718C..0x171A0`. PA5/PA6/PA7 directions are consistent with candidate SPI1 SCK/MISO/MOSI assignments, and PA0/PA4 are consistent with the selector writes above. This conditional configuration match does not establish alternate-function remapping, PCB nets or actual connections to two MCP2515s. No physical registers were read or modified.

The SPI WRITE path at `0x168DE` treats incoming `a0` as a bit mask: bit 0 causes a `0x10` write to `0x40010814`, and bit 1 causes a `0x01` write there. It then transmits `0x02`, the address and data; on normal completion it writes `0x11` to `0x40010810`. If those GPIOA addresses implement the WCH bit-clear/bit-set registers and the nets are active-low chip selects, this corresponds to selecting PA4/PA0 and releasing both at the end.

The function checks only the low two bits and does not reject 0 or 3 locally: 0 skips both selection writes but still transmits, while 3 requests both selection writes; higher bits are ignored by these two tests. This is a conditional interpretation of original instructions and the candidate GPIO interface. It does not show callers actually supply those values, what components the nets reach, their electrical polarity or hardware safety. Neither the function nor hardware was executed.

The identified caller at `0x16CC4` first checks `((a0-1)&255)<=1`; passing means the input's **low byte** is 1 or 2, not necessarily that the entire 32-bit value is exactly 1/2. It saves the original `a0` in `s0` and passes `s0` to `0x168DE` at `0x16D70..0x16D7E`. If the intervening two indirect slots and other callees return normally and preserve `s0`, the low two bits at this call can only be `01` or `10`: under the candidate GPIO interpretation, one line is selected per call, not the theoretical 0/3 cases above. This covers only this caller and does not establish other callers' ranges, iteration count, the physical chip or successful transmission.

Another record path at `0x16B7C` applies the same 1/2 guard to the byte at record offset 11; after it passes, the code also checks other configuration and record length. At `0x16C18` it **freshly rereads** offset 11 and passes it to `0x168DE` at `0x16C2C`. The entry guard can therefore be extended to that SPI WRITE call only if the record pointer/content is not altered by intervening calls, aliases or asynchronous paths and the calls complete normally. The original code does not repeat that guard immediately beside the fresh read. This does not establish the actual record producer, CS wiring or successful transmission.

A third wrapper `0x16B50` indexes bytes at a stack halfword containing `0x2420` using incoming `a1` as the SPI address, then passes original `a0` to `0x168DE`. The identified `0x16E88` path supplies `a1=0/1` at `0x16ED0/0x16ED8`, so under little-endian and valid stack/callee contracts the addresses are `0x20/0x24` respectively. This local bound does not mean the wrapper itself validates arbitrary indices.

At both calls `a0` comes from the original input to `0x16E88`, subject to `0x16E0C` returning zero and intervening control flow, but the reviewed `0x16E88/0x16E0C` bodies do not directly restrict that input to 1/2 as the two paths above do. If preservation and memory contracts hold, the chip-select low bits follow that input; this does not prove that 0 or 3 is reachable from an actual caller or that all calls select only one chip. Neither target nor hardware was executed.

A further check of four identified direct calls finds `0x16F38` and `0x16F86` call `0x16E88` with `a0=1`, while `0x16F6C` and `0x16F8E` use `a0=2`. Each call is gated by event-mask, counter or earlier-return branches in `0x16F00`. If `0x16E0C` returns zero and all intervening calls return normally, preserve `s0` and keep the stack valid, the selector at the two `0x16B50` calls remains 1 or 2 respectively. This narrows those four identified direct call sites; it does not exclude other unrecognized entries, indirect callers or physical wiring differences.

Before those configuration writes, `0x16E0C` performs candidate GPIO selection according to selector bits, transmits `0xC0` through `0x16896`, then requests release of both candidate lines. It repeatedly calls `0x16994` at address `0x0E`, returning 0 only when `(value&0xE0)==0x80`; it returns 1 if the unsigned `0x81B0` time difference exceeds 2. `0x16E88` proceeds to its later configuration, including the `0x20/0x24` writes above, only after receiving 0.

This is consistent with the prior MCP2515 candidate reset/status context. `0xC0`, `0x0E` and the mask are original operands, not independent proof of the physical chip, time units, effective chip select or successful initialization. The timeout exit depends on changing clock results and normal calls; no hardware test was performed.
