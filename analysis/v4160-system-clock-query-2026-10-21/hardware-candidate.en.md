# WCH CH32V20x candidate

Recorded2026-10-21. The user supplied the lead that TSL6 uses WCH CH32V20x RISC-V and requested it as a TSL9 reference. The [TSL6 reference repository](https://github.com/jfryton/TSL6-Firmware) also identifies that family for TSL6. This supports a family hypothesis without identifying a TSL9 board or exact part.

| Evidence | Observation and limit |
| --- | --- |
| Original ID2966 V4.1.60, SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667` | Source18838 reads40021004; source1889E reads40023800. These are static numeric observations. |
| [Official WCH CH32V20x header](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32v20x.h) | RCC/CFGR0 and EXTEN addresses match those observations. A shared register map is not unique chip identification. |
| [Official CH32V208 information](https://www.wch-ic.com/products/CH32V208.html) | Wireless support and a64KB SRAM option make this a useful subfamily candidate; package and configuration remain unknown. |
| Current reset/entry dataflow | Numeric GP20004000 and SP20010000 are consistent with a64KB SRAM hypothesis, without measuring physical RAM. |

Continue exact source comparisons for startup, clock, interrupt and resident interfaces. Preserve variant differences. This reference neither closes the resident UND nor establishes pin wiring, installed ROM ABI or BLE OTA compatibility. Chip markings are unavailable; ongoing offline work does not require a repeat request or physical access.
