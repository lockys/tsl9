# CH32V208 QingKe V4 interrupt vector comparison

[繁體中文](README.md)

Original ID2966 V4.1.60 reset writes `0x803B` to `mtvec` at `0x18718..0x1871C`: BASE=`0x8038`, MODE=`3`. A user-provided close-up of the original board shows CH32V208GBU6 marking; the [WCH product page](https://www.wch.cn/products/CH32V208.html) identifies CH32V208 as using QingKe V4C.

Section 3.2 of the [official WCH QingKe V4 manual](https://www.wch.cn/uploads/file/20220411/1649641123177990.pdf) describes MODE=`0b11` as using absolute handler addresses stored in a vector table indexed by interrupt number times 4. Under that official contract, original APP BASE and the existing [IRQ enum/vector evidence](../tsl9-trap-profile-contract/readme.en.md), the mapping is:

| Official enum | Number | `0x8038+4×number` | Original APP table word |
| --- | ---: | --- | --- |
| USB_LP_CAN1_RX0 | 36 | `0x80C8` | `0x12C24` |
| EXTI9_5 | 39 | `0x80D4` | `0x16FB6` |
| TIM3 | 45 | `0x80EC` | `0x979E` |
| BB | 63 | `0x8134` | `0x1873E` |
| LLE | 64 | `0x8138` | `0x8498` |

This narrows the earlier documentation's statement that official mode-3 semantics were unknown: **the official V4 specification provides those semantics**. This remains conditional reasoning from the chip marking, manual and original APP bytes; it does not observe actual `mtvec`, PFIC state, vector remapping, interrupt delivery or execution order. The WCH manual also describes separate mechanisms such as VTF, so the ordinary vector formula does not establish every possible interrupt path. Slot binding, ROM and IRQ compatibility remain unverified. No firmware execution or hardware operation occurred.
