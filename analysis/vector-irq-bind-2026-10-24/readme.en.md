# Bind vector39 to the genuine IRQ provider

[繁體中文](README.md) · [Results](summary.json) · [C/C++ source](../../src/native/irq/irq_flag.c)

The existing complete16FB6–17002 C/C++ handler is reused:76B/21 instructions equal the original, including its final MRET. Source and manifest remain unchanged.

Vector slot39 (original80D4, value16FB6) now binds the genuine76B function through a section-relative label. The zero-size alias shares the actual section/offset with a full-size provider; no empty handler or ABS address substitute is added.

| Genuine partial link | Result |
| --- | --- |
| Code/data | 648B/233 original instructions plus456B data; prior572B code and456B data unchanged |
| Symbols/references | 100 nonzero architectural FUNC regions,1 explicit FUNC alias,144 RELA and7 UND |
| Vectors | 56 slots bind real code;6 slots still reference5 external entries |
| Verification | Identical C11/C++17 products; current108 source comparisons/216 objects still pass |

The [local SDK comparison](hardware-sdk-match.json) finds three correspondences: saved CH32V20x EXTI9_5_IRQn39, EXTI_BASE40010400 and INTFR offset14 match original vector39 and access40010414. This supports a compatible EXTI-layout inference, **not physical chip or GPIO-pin identification**. Mask-write clearing semantics still require peripheral documentation or implementation evidence.

The original independently reads status, tests40/80, and ORs1/2 into then-live GP+360. Per-source IRQ diagnostics are a feature candidate; no counter, extra MMIO or BLE operation is added.

Remaining entries are8448,8498,979E,12C24,19BD4,main9008 and resident40000. Matching the MRET body does not prove register-save, nesting/fault or installed-ROM context compatibility. The82 stored words do not establish physical IRQ count.

This is a VMA0 ET_REL. Its provider is at diagnostic code offset572, **not original execution address16FB6 and not a flashable BIN**. Final original placement, hardware/memory identity, complete IRQ/main/ROM and BLE OTA remain unproved.

The [three-original receipt index](publication-provenance.json) preserves exact local evidence bytes. See [experiment/replay](../../experiments/tsl9-vector-irq-bind/readme.en.md). No target/HOST execution, ISA emulation or hardware/network operation occurred. Commit/push remain held for historical personal information.
