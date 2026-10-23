# Peripheral writer18CA4: offline C/C++ reconstruction
[繁體中文](readme.zh-TW.md)

Selected `src/peripheral_write.v2.c`; curated repository copy `src/native/receive/peripheral_write.c`. Original `[0x18CA4,0x18D78)` is212B/72i, including three reachable post-RET cold blocks. C owns arithmetic and volatile memory; empty register ports plus seven symbolic edge/RET ports preserve architecture and placement. The seven regions are not independently callable ordinary C ABI functions.

Preserves:
- Up to three distinct fresh statusword reads, short-circuiting bit26/27/28. No selection returns4 before dereferencing the record.
- First bank+384 write is oldvalue AND1. ID paths retain complete input bytes8/9, without boolean normalization or extra ID masks.
- Inputbyte10 AND15 is written back before two separate fresh bank+388 RMWs. No DLC<=8 guard is added.
- Payload read order12,11,13,14,16,15,17,18; always eight bytes. Final fresh control value is ORed with1.
- A2 retains the first three bytes of the second payload word; A4 retains final fresh control OR1. A6 is written only on the alternate path; no-selection A2/A6 remain inherited.

One RV32IMAC_Zicsr/ILP32/Oz profile builds C11/C++17. Native output has seven genuine FUNCs, seven local pending RELAs and zero UND/global ABS. Native typed equality covers non-relocated fields, with targets checked through genuine symbols; raw immediates are still pending. Nominal original-address linking resolves all seven controls and matches every original212 byte. Nominal equality is not physical installation.

Each formal `build/verified-v2/{c,cpp}/verification.json` passes197 negatives:144 native/linked instruction mutations,10 symbol,2 whole-file tail,21 RELA,14 IR,5 source,1 MD;195 do not rely on whole-ELF hashes. Complete IR (only ModuleID/source_filename removed), ordered C operations,22 static loads/eight stores, two MD inputs, five actual recipes and13 inputs are checked. Branches do not execute all22 static loads together. No target/ISA/MMIO execution.

[source-history.json](source-history.json) retains both sources and raw outputs. v1 had compiler-reordered blocks and is not selected; v2 retains original placement. The first formal attempt failed because a negative test searched for an assembly mnemonic for a C-emitted IR load. Its original spec is archived; only one negative anchor changed, with source/flags unchanged.

```sh
python experiments/tsl9-peripheral-write/verify.py --language c --out-dir experiments/tsl9-peripheral-write/build/verified-NEW/c --llvm-bin "$LLVM"
python experiments/tsl9-peripheral-write/verify.py --replay experiments/tsl9-peripheral-write/build/verified-v2/c/verification.json --llvm-bin "$LLVM"
```

`--require-firmware-ready` must exit1. Trusted Python standard-library runtime is not a hermetic input closure. Peripheral identity, caller/resident ABI, alias/asynchronous behavior, full startup/ROM/IRQ and BLE OTA compatibility remain unknown. No flashable BIN is produced.
