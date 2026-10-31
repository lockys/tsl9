# CH32V208 clock startup: original instruction comparison

[繁體中文](README.md)

The target is original ID2966 V4.1.60 `0x1874A..0x18834`. The [existing full clock audit](../tsl9-clock-reset-noninterference/readme.en.md) records equality of these 234 bytes with original-address C11/C++17 diagnostic ELFs. This page identifies bit operations against the [official WCH header](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32v20x.h); no live registers were read.

| Original location | Instruction observation and WCH definition |
| --- | --- |
| `0x1874A..0x1875A` | Sets bit 0 at `0x40021000`, corresponding to `RCC_CTLR.HSION`. |
| `0x18794..0x187B4` | Sets `0x10000` and polls `0x20000` at the same address, corresponding to `HSEON` and `HSERDY`. A counter starting at 0 can stop the loop at `0x1000`; the status is then read again. |
| `0x187BC..0x187CE` | Rechecks the ready bit; when clear, the route through `0x18830` returns without executing the PLL configuration below. |
| `0x187FC..0x1880C` | Sets `0x01000000` then polls `0x02000000`, corresponding to `PLLON` and `PLLRDY`. No local timeout was observed in that loop. |
| `0x18810..0x18828` | Sets the low two bits of `0x40021004` to 2, then waits for `(value & 0x0C)==8`, corresponding to PLL selection and `SWS_PLL`. No local timeout was observed in that loop. |

The normal HSE-ready path enters PLL configuration and polling. Status is read again after the first loop, so reaching the counter limit does not by itself prove failure. PLL-ready or switch-status loops may continue indefinitely depending on hardware; static instructions do not prove startup success, actual clock frequency, GPIO wiring or IRQ behavior. The official D8W default HSE constant is 32 MHz, an SDK setting rather than a measured frequency.

The photographed marking supports CH32V208GBU6; memory mapping, option bytes, installed ROM, clock and physical connections remain to be verified. No target execution or hardware connection occurred.

## Conditional frequency comparison

At `0x187EE`, the code masks `CFGR0` with `0xFFC0FFFF`, then ORs `0x00290000` at `0x187F4..0x187FA`. The latter combines the official HSE PLL source `0x00010000` and PLLMULL12 `0x00280000`. The earlier `0xFF80FFFF` mask at `0x18786` clears these PLL fields; without intervening modification, the setting matches the [WCH 96 MHz example](https://github.com/openwch/ch32v20x/blob/main/C%2B%2B/Use%20MRS%20Create%20C%2B%2B%20project-example/CH32V203C8T6%2B%2B/User/system_ch32v20x.c).

For D8W / CH32V208 the official example describes `32 MHz / 4 × 12 = 96 MHz`. The original path first clears the low 16 configuration bits and sets `PPRE1_DIV2` at `0x187E6`. If no intervening writes occur, HSE is actually 32 MHz, and PLL ready and clock switching succeed, the example implies SYSCLK/HCLK 96 MHz, PCLK1 48 MHz and PCLK2 96 MHz. This is a **conditional configuration inference**, not a measurement, proof of oscillator frequency, unchanged settings, or path completion.

## Conditional SPI1 initialization comparison

Original `0x1716C..0x1719A` builds stack data and calls `0x196C4` with `0x40013000` and that data; the callee ORs the first eight halfwords into a control register and writes the ninth at offset 16. Interpreted using the [WCH SPI structure and constants](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32v20x_spi.h), the values correspond to master, two-line full duplex, 8-bit, low CPOL, first edge, software NSS, MSB first and **divide by 8**. `0x1719A..0x171A0` then requests enable. This static comparison depends on the initialization path, register mapping and settings remaining unchanged.

If the previous section's 96 MHz PCLK2 conditions also hold and SPI1 actually uses that APB2 clock, divide by 8 implies **12 MHz SCK**. A chip on the photographed board is legibly marked MCP2515; the [Microchip datasheet](https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MCP2515-Family-Data-Sheet-DS20001801K.pdf) specifies a 10 MHz SPI maximum under its tabulated conditions. This is a conditional discrepancy to investigate, not a 12 MHz measurement or proof of PCB connectivity, an actual specification violation, or malfunction. The clock path, later reconfiguration and board signals are unverified. Do not modify or flash firmware based on this alone.

The helper `0x1971E..0x1973C` called at `0x171A0` sets control bit 6 on the nonzero-argument path, preserving the remaining bits including the divider field. The compared transfer helper `0x16896..0x168DE` polls and reads/writes only SPI status/data offsets 8/12; it does not modify the control register in its own body. Each wait exits after a counter initialized to 255 expires, but that count is not a known duration. Both timeouts and a normally received `0x00` return the numeric value 0. These findings narrow only those two local functions; other code, indirect calls or asynchronous paths may reconfigure the clock or SPI.
