# Resident memory leaves: complete reserved-register recipes

[繁體中文](readme.zh-TW.md) · [English](readme.en.md)

Real C/C++ compilation derives exactly one allocator bank per leaf from original own-written GPRs plus the three explicit A0/A1/A2 inputs. **The recipes still fail the original ABI:** avoiding the previous extra allocatable scratch writes makes LLVM use RA and a 16-byte stack frame; fill also transiently writes A2. This is a retained native compiler experiment, with no flashable BIN.

| Selected entry | Original bytes | New bytes / instructions | Own-written GPRs | Whole ET_REL bytes / instructions |
| --- | ---: | ---: | --- | ---: |
| compare 200004BC | 62 | 60 / 23 | RA, SP, A0, A3, A4, A5 | 454 / 171 |
| fill 2000039C | 46 | 68 / 24 | RA, SP, A0, A2, A4, A5 | 492 / 187 |
| copy 20000332 | 58 | 64 / 22 | RA, SP, A3, A4, A5, A6 | 418 / 155 |

Six real ET_REL objects compile successfully. Selected machine bytes match between C and C++ for each leaf. Each complete object honestly retains eleven genuine global FUNCs, ten unused for its selected-entry assessment; no linker removal is assumed. All objects have UND=0, RELA=0 and no ABS provider. Whole-object sizes include those unused functions.

The allocator universe is x5..x31. Reserve its complement of (original own-written GPRs union x10/x11/x12), using -ffixed-xN flags explicitly supported by actual compiler help. Allowed banks are x10..x15 for compare, x10/x11/x12/x14/x15 for fill, and x10..x16 for copy. Dedicated x0/x1/x2/x3/x4 are inspected separately; their role does not authorize RA/SP writes. A2 is an allocator input but fill's original own-write contract still forbids transient changes: those two sets are not conflated.

The wrapper includes sealed native.c unchanged; it in turn includes the unchanged shared algorithm. Original fixed -Oz, rv32imac_zicsr_zifencei, ilp32, no-outliner and other flags remain, adding only each single derived fixed-register bank. No mask sweep, fake provider, numeric ABS, encoder or opcode template is used. No visibility/internalization rewrite was required.

Stack/RA writes precede guard MMIO, unlike the original frameless leaves. Normal restoration cannot prove transient register/stack or fault/asynchronous-prefix equivalence. Independent ABI review assesses exact scratch liveouts and A0 timing around byte faults. Full ABI, placement, installed-provider and physical OTA proof remain false. Fill/copy exceed original extents; shorter compare does not prove tail ownership.

**Compile and static inspection only. Never execute on HOST:** real volatile MMIO and FENCE.I are present. No HOST test-matrix rerun, RV32/ISA/MMIO/hardware execution, link, objcopy, BIN, flashing or third-party network occurs.

## Portable entries and evidence

```sh
sh experiments/tsl9-resident-register-contract/verify.sh --project-root "$PWD" --tool-dir LLVM
python3 CASE/implementation/check.py --project-root ROOT
python3 CASE/implementation/probe.py --project-root ROOT --replay LEAF/LANGUAGE/verification.json
python3 CASE/implementation/check.py --project-root ROOT --receipt LEAF/LANGUAGE/verification.json
```

CASE is workspace apk-analysis/tsl9-v4160-register-contract-2026-10-22 or delivered analysis/v4160-register-contract-2026-10-22. Python/sh entries are portable; this round admits only existing pinned Windows NDK 27.1 hashes, without claiming other compilers match. Fresh --build-root must be create-only beneath model/build; omission uses a UUID. Each run produces three leaves times C/C++: six archives. Default check reads source/metadata only. Explicit receipts inspect actual object, IR, MD, complete disassembly, compiler/resource identities and all logs, without recompiling or executing.

Current archives are build/reserved-bank-v1-portable/{compare,fill,copy}/{c,cpp}. Initial build/reserved-bank-v1 raw outputs and initial-probe-snapshot.py remain historical diagnostics. Only probe delivered-directory lookup and pre-compilation help validation were repaired, then the exact same masks/source/flags rebuilt current receipts. Historical receipts cannot be presented as current-probe replay. No second semantic source/recipe profile was introduced.
