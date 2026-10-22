# NV write callback, timer and genuine C/C++ component

[繁體中文](README.md) | [English](readme.en.md)

Original V4.1.60 / ID2966 callbacks `0x197BE` and `0x19764` are reconstructed in real C11/C++17, sharing six genuine Flash C helpers. Each complete object retains eight global FUNCs,394B/148 instructions, UND0/RELA10. The write entry is72B/26 instructions/16B frame; the timer is60B/23 instructions/frameless. C/C++ code bytes agree.

The write calls unlock, erase, program, lock, delay(1), then returns zero. Entry A2 supplies the source; A1 is unused. The timer uses a fresh GP+382 byte and low32-bit product, with at least12 ordered volatile effects around `0xE000F000` and unbounded polling until STATUS bit0 is set. Physical time units remain unproved.

Independent original-source review reads294B/115rows/six groups and rejects seven raw controls. A separate44B/12row calibration relation rejects seven controls: `GP+382=(READ32(GP+108)/8000000)&255` feeds the timer only under same-GP/no-intervening-write premises. Its44B includes4B already counted in the timer review, not44 additional unique bytes.

Independent native review checks complete ELF/raw operands, LLVM static output and C IR, rejecting12 controls per language. Real ld.lld linking retains all eight C definitions in an offline ET_EXEC, resolving ten calls with no UND, remaining RELA or ABS providers. One RX LOAD covers exactly394 code bytes; a non-LOAD RISC-V attributes header is metadata. Independent component review checks260 relocatable immediate bits,24 actually changed bytes and seven malformed real-ELF controls. Linked code SHA256: `bc6c4438642ee15072836bb30b7e97fdff168b1c49bda5fe9ce9fdde58283aca`.

**No new firmware BIN; this component is not flashable.** VMA0 is a nonphysical offline layout. The write frame/source retention, timer output registers and extra unlock/erase A1 writes differ from the original. The retained unused quarter asm-call declaration omits those two A1 clobbers; no observed read-before-reload counterexample in this fixed object does not prove its compiler contract complete. Full ABI, fault/IRQ, startup/GP/stack, installed ROM/Flash/NV ownership and BLE OTA remain unproved. No native/CPU/ISA/ESIL/hardware execution or unchanged HOST-matrix rerun occurred. Existing images remain unchanged.

## Sources and implementation

- [Shared C/C++](../../experiments/tsl9-nv-write-callback/readme.en.md)
- [Actual compilation and source freeze](implementation/readme.en.md)
- [Original source](source-review/readme.en.md)
- [Independent native review](native-review/readme.en.md)
- [Calibration relation](calibration-review/readme.en.md)
- [Actual offline component link](component/readme.en.md)
- [Independent component review](component-review/readme.en.md)

Feature proposal: offline diagnostics for zero/truncated/wrapped calibration bytes and GP calibration lifetime. This is not an integrated hardware feature. Next, repair the clobber contract in a new owned profile and trace original-caller registers; preserve old seals.
