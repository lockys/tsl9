# ADC complete register bank for one evidenced caller

[繁體中文](readme.zh-TW.md) · [English](readme.en.md)

A new C translation unit ordinarily includes sealed ADC native.c. The C core, genuine volatile ports and A0/A1 bridge remain unchanged. Exactly one caller-derived complete bank is added to the fixed NDK/-Oz/rv32imac_zicsr_zifencei recipe, with actual C11/C++17 compilation. No HOST matrix is rerun and native code never executes.

Prior source-review post_config_register_liveness establishes that this caller overwrites A0..A6 before reading them. A7 and T0/T2/T3/T4/T5/T6 survive to normal exit; T1 exits with 15. The sole allowed bank is therefore **x10..x16**, reserving its complete complement within x5..x31. Dedicated x0/RA/SP/GP/TP are checked separately; their role does not permit arbitrary writes. Actual complete clang --help confirms every -ffixed-xN RISC-V option before compilation.

## Actual outputs

Both C/C++ compile successfully. All five corresponding function byte strings match, and both real artifact archives pass read-only replay.

| Genuine global FUNC | Bytes / instructions | Status |
| --- | ---: | --- |
| tsl9_adc_config_1892e | 110 / 42 | Selected entry; no call |
| tsl9_adc_config_io | 132 / 50 | Unselected genuine context/sret core |
| ml_port_read32 | 8 / 4 | Unselected genuine volatile port |
| ml_port_write32 | 6 / 3 | Unselected genuine volatile port |
| ml_port_read8 | 10 / 4 | Unselected genuine volatile port |

Whole ET_REL: **266B / 103 instructions / five globals; UND=0, RELA=0, no ABS provider**. No linker removal of the four unselected functions is assumed. No actual function writes any fixed-bank register.

The selected entry writes **RA/SP/A2/A3/A4/A5/A6**. A7 and all T registers remain untouched, but LLVM introduces a **16-byte frame**: subtract 16 from SP, store RA at entrySP-4, borrow RA for the first WORD read, restore RA from that slot and add 16 before return. A0/A1 have no own writes; S/GP/TP are untouched. These extra stack/RA effects cannot be hidden as matching the original frameless ABI.

Public LLVM IR retains ten volatile WORD reads, one BYTE read and three WORD writes in source order. Complete disassembly separately exposes the RA stack store/load: the fourteen target effects are not all machine memory effects.

Original callee: 88B / 37 instructions; the new entry exceeds it by 22B. Original own writes are A3/A4/A5; RA/SP/A2/A6 remain additional writes and scratch liveouts differ. This producer does not admit the specific caller's normal projection itself. Independent ABI review must separately establish normal return, private stack disjoint from config/targets, absence of observers of entrySP-4 and the caller's overwrite chain. Even a valid bounded projection does not prove full original callee ABI, fault/IRQ/asynchronous equivalence, placement or installed-provider identity.

## Running and evidence

```sh
sh experiments/tsl9-adc-caller-bank/verify.sh --project-root "$PWD" --tool-dir LLVM --build-root NEW
python3 CASE/implementation/check.py --project-root ROOT
python3 CASE/implementation/probe.py --project-root ROOT --replay MODE/verification.json
python3 CASE/implementation/check.py --project-root ROOT --receipt C/verification.json --receipt CPP/verification.json
```

CASE supports workspace apk-analysis/tsl9-v4160-adc-caller-2026-10-22 and delivered analysis/v4160-adc-caller-2026-10-22. NEW must be create-only beneath model/build; omission uses UUID. Current W archives are build/caller-bank-v1/{c,cpp}, retaining actual tool/resource/header hashes, seven MD inputs, complete IR/disassembly, help, raw logs and receipts. Default check reads source/metadata only. Explicit receipts reread actual artifacts without recompilation or execution.

Exactly one bank/source/recipe is used. No mask/flag sweep, handcrafted opcode, stub, fake provider, numeric ABS, native link, BIN or flashing occurs. Never launch genuine volatile MMIO code on HOST. There is no RV32/ISA/MMIO/hardware execution or third-party network operation. Python/sh sources are portable; native results admit fixed Windows NDK hashes only. The previous Git Bash launch denial is not retried, so sh runtime remains unverified. Newly authored source/docs use LF, one EOF newline and Git-style whitespace checks; actual raw compiler logs remain unchanged.
