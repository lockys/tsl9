# Original peripheral initializer and descriptor

[繁體中文](README.md) · [C/C++](../../src/native/can/peripheral_initializer.c) · [Original instructions](evidence.json) · [Summary](summary.json)

Complete18AB0–18BA2 adds242B/99 instructions,27 private regions and17 control relocations,including six clear branches after the firstRET. It makes no external calls. The real main-initializer entry is resolved;missing providers76→75. Existing adjacent filter18BA2 and IRQ helper18CA4 implementations remain unchanged.

The function clears controlbit1,setsbit0,and polls statusbit0 with initial counter65536,then reads status again. Missing entry acknowledgment returns0. Six flags compare full32-bit words to exactly1; all other values follow original clear branches,not low-byte or general nonzero tests.

|32B descriptor field|Original operation|
|---|---|
|halfword+0|Subtract1 and OR,without new masks or range checks|
|byte+2/3/4/5|Shift left30/24/16/20|
|word+8/12/16/20/24/28|Exactly1 sets controlbit7/6/5/4/3/2;otherwise clears|
|byte+6/7|Unread by this function;retained in type|

The packed value is written at base+28. It then clears controlbit0,polls statusbit0 with another counter65536,and returns(~fresh_status)&1. Counters are not milliseconds. Physical success,peripheral clock,CAN bitrate and MCU identity remain unproved.

A descriptor type in the C/C++ source has seven compile-time assertions for32B size and original offsets. This proves the selected RV32 compiler's type layout,not physical hardware or the whole private ABI. No descriptor model or peripheral code was executed.

115 C/H files and88 code units pass178 comparisons/356 objects including independent pointer data. Previous114 sources and1045 artifact records are preserved. The component contains20988B code+714B data;all21702B match the official ID2966 BIN at native original addresses,with75 genuine providers still missing.

Flow covers7287 instructions,1200 direct transfers(1125 measured/75 reference-only),6728 ordinary next positions without gaps,and448 potential call-return positions.374 register-indirect transfers,10MRET and1EBREAK remain short of a complete CFG or physical proof. Diagnostic ELF entry0/PT_LOAD0 is not flashable.

Component-v1 inherited a plural receipt-field label. It was corrected and a fresh component-v2 was generated with identical machine bytes;no source or audit guard changed,and old artifacts remain. Next:privacy review of six settings fallbacks. A proposed offline descriptor/clock-contract inspector is not implemented and would not guess physical bitrate. No target/HOST-model/ISA execution,hardware or network actions occurred. Historical privacy findings keep commit/push held.
