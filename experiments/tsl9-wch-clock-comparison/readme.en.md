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
