# Resident startup and ROM configuration

[繁體中文](README.md) · [English](readme.en.md)

Eight complete functions add **1,082B /385 instructions**,plus21B of public version-prefix data. Two old startup imports now have real bodies;22 ADC/clock/MAC/delay dependencies are exposed. There are165 genuine imports remaining. No firmware BIN was generated or hardware accessed.

| Static evidence | Result |
| --- | --- |
| Standalone C11 /C++17 | Same object;74 code regions,one21B readonly object,66 RELA,52 direct controls,seven typed address pairs |
| Curated sources | 129 C/H;204 function/code-unit comparisons plus2 independent data comparisons =206 comparisons /412 objects |
| Main component | 38,454B code +1,771B data;13,408 instructions;3,193 FUNC,71 retained zero-size aliases,14 readonly objects,2,534 RELA |
| Original addresses | All40,225 selected bytes match the official BIN;3,207 owners in112 adjacent-only spans |
| Transfers | 2,250 direct transfers;817 call-return positions;zero ordinary continuation gaps |
| Semantic witnesses | 201 reviewed opcodes and8 address calculations |
| Independent saved SDK candidate | Two240B metadata objects;zero FUNC/relocations/imports;not linked into the main component |

The image compares21 bytes against **CH32V20x_BLE_LIB_V1.3** at1AB1C. This confirms the image's expected library prefix and supports the CH32V20x family candidate. It does not identify the physical MCU/package or prove the installed ROM version.

Confirmed instruction behavior:

- 199E2 preserves the version-result loop19A08,the fresh heap pointer/length check loop19AE0 and initialization-result loop19AF0. None was bypassed.
- It constructs a64-byte config atSP+16,including heap address2000418C/length0x7000,SNV address0x08077C00,packed values0x0803 and0x0E3F,length251,event count3,and frequency/accuracy fields16000/1000. Six dynamic scratch bytes are copied into offset24;no device MAC was read.
- Callback assignments point to1979A(read),197BE(write),197F0(sample) and197B8(calibration). The saved header gives these candidate names;installed implementation/private ABI is unproved.
- 1979A forwards a word-scaled copy to ROM slot76. 197BE preserves its original saved-entry-A2 reuse for both A1 and A2 at18EF2;SDK callback ABI conformance is not claimed or repaired.
- 197F0 preserves encoded RCC/peripheral backup/restore fields and the original polling loop. 1995C preserves event priority15/0/13/14,full-width event XOR results,message handling and scheduling tuples.
- 19B16 registers1995C,stores the returned task byte and invokes19B56. The latter builds a16-byte candidate timer config,keeps all setup calls and invokes slot116. Existing RTC interrupt19BD4 was retained.

Independent native data-only compilation confirms saved SDK `bleConfig_t` size64 and `bleClockConfig_t` size16,alignment4,and all field widths/offsets. Eighteen original stack stores,including compressed C.SWSP,and the six-byte copy loop agree with those offsets. The two metadata objects are separate from the206/412 main source proof. No SDK function was executed.

The code uses register-bound C and explicit architecture ports. Physical silicon,ROM contents,heap reservation,RAM/Flash capacity,asynchronous ABI/IRQ binding,clock units and BLE OTA compatibility remain unproved. The opaque default and20 prior static payload references remain unprovided;the full authentication body stays private/unresolved. The diagnostic ELF has entry0 and no PT_LOAD.

[Instruction/data evidence](evidence.json) · [Contracts](provider-contracts.json) · [Measured summary](summary.json) · [Remaining providers](next-providers.json) · [Feature candidates](feature-candidates.json)

[Selected source](../../src/native/startup/resident_startup.c) · [Native recipe](../../experiments/tsl9-resident-startup/spec-v1.json) · [Source proof](../../experiments/tsl9-resident-startup/verify-source-v1.py) · [Integration recipe](../../experiments/tsl9-resident-startup/integration-v1.json) · [Layout recipe](../../experiments/tsl9-original-layout/spec-v32.json) · [Flow verifier](../../experiments/tsl9-original-layout/verify-flow-v35.py) · [SDK layout recipe](../../experiments/tsl9-resident-startup/sdk-boot-layout-v1.json)

From the repo root,with the existing pinned local tools and retained receipts:

```sh
python3 -B experiments/tsl9-original-layout/verify-flow-v35.py --replay experiments/tsl9-original-layout/build/resident-startup-flow-v1
python3 -B experiments/tsl9-resident-startup/verify-sdk-boot-layout-v1.py --tool-dir "$LLVM_BIN" --sdk-header "$SDK_HEADER" --replay experiments/tsl9-resident-startup/build/sdk-boot-v1
```

`LLVM_BIN` and `SDK_HEADER` are user-provided local paths. Raw receipts,saved SDK header and superseded trials stay local. No target,host model,ISA emulator or flashing was executed.
