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

## Startup `INTSYSCR` configuration

Original reset loads 3 at `0x186FE` and writes it to CSR `0x804` at `0x18700`. Section 3.2 of the same WCH V4 manual names this CSR `INTSYSCR`: bit 0 `HWSTKEN=1` requests hardware stacking and bit 1 `INESTEN=1` requests interrupt nesting. However bits 3:2 `PMTCFG=0` are defined in the manual's table as no preemption bits / no nesting. Setting bit 1 alone therefore does not establish that nested interrupts occur on the device.

In this written value bit 4 `HWSTKOVEN` and bit 5 `GIHWSTKNEN` are both 0. The manual describes bit 5 as a global-interrupt and hardware-unstack disable control used during interrupt context switching, automatically cleared after interrupt return. This supplies the official bit-5 meaning missing from the earlier [numeric contract](../tsl9-trap-profile-contract/readme.en.md); it does not establish physical execution of later `0x8448` or interrupt return, unchanged control bits afterwards, or stack/IRQ safety.

## Ordering of `mstatus` and vector setup

Original `0x18704..0x1870C` constructs `0x1888` and executes `CSRRS mstatus`; this ORs the mask into the old value rather than replacing the whole CSR with `0x1888`. Under the same WCH V4 manual's `mstatus` field definitions, the mask sets MIE bit 3, MPIE bit 7 and MPP bits 12:11=`11`; other writable bits retain their prior values. The manual identifies MIE as machine interrupt enable, MPP=`11` as retaining machine mode on return, and `mret` as restoring execution and state from the then-current `mepc`/MPP/MPIE.

This OR occurs **before** the new `mtvec` write at `0x1871C`; `mepc=0x9008` is only written at `0x1872C`, followed by the jump to `0x40000` at `0x18730`. Therefore, without absence of deliverable interrupts or another effective masking condition, the sequence alone cannot establish that no interrupt occurs before the new vector setup; it does not establish that one actually occurs either. Candidate resident `mret` reaching `0x9008` additionally requires `mepc` not to have changed and a compatible resident path. This is a static specification/instruction comparison; no live CSR or hardware execution was observed.
