# Resident memory: real volatile native adapters

[繁體中文](readme.zh-TW.md)

Compilation/static inspection only. **Never execute this adapter on HOST:** it contains actual volatile MMIO and FENCE.I. The sealed shared algorithm is included as ordinary C source, without original bytes, opcode templates or callback stubs. No link/BIN, hardware, RV32 or ISA execution occurs.

Public entries take three u32 arguments and return u32. The second and final profile measures:

| Entry | Original candidate bytes | New entry bytes | Remaining examples |
| --- | --- | --- | --- |
| compare 200004BC | 62 | 52 | Extra write to original-preserved A6; scratch liveouts differ |
| fill 2000039C | 46 | 48 | Extra A3/A6/A7 writes; two bytes larger than original |
| copy 20000332 | 58 | 52 | Extra T0/A7 writes; other scratch values differ |

The three selected entries total **152B**. Actual outputs have no frame, call, context or sret and never write A1/A2/SP/S/GP/RA. They contain guard save/zero/FENCE.I before null/count tests, fresh byte effects and saved-word restoration. These bounded improvements do not prove the full original register/fault/asynchronous prefix ABI. Shorter compare/copy bodies do not establish tail ownership; fill cannot fit its original 46B extent. Fixed placement and installed-provider admission remain false.

The complete ET_REL honestly retains eight additional globals totaling **230B**: three context/sret algorithms (64/62/64B) and five genuine I/O functions (10/6/8/8/8B). No linker removal is assumed. Complete allocation is **382B / 138 instructions, zero UND and zero RELA**, not the sum of selected entries.

## Two actual profiles

Ordinary wrappers are 30B each but allocate 64B frames, call context/sret algorithms and overwrite A1/A2. Their complete object is 320B /125 instructions /3 CALL_PLT. This failed diagnostic and source snapshot remain local under build/ordinary-v1; current sources cannot be presented as a current-root replay of that historical receipt.

The sole second adaptation adds source always_inline declarations and an empty-asm read/write A0/A1/A2 return bridge. Shared algorithm bodies remain unchanged; actual IR/machine output proves context elimination. I/O functions perform real volatile byte/word accesses and return 1 only after normal completion; hardware faults/traps do not fabricate cleanup. zifencei is added specifically for real FENCE.I; other pinned -Oz flags are unchanged. No third profile/flag sweep or unchanged HOST rerun occurs.

## Portable entries and evidence

```sh
sh experiments/tsl9-resident-memory-native/verify.sh --project-root "$PWD" --tool-dir LLVM --language both
python3 CASE/implementation/probe.py --project-root ROOT --replay MODE/verification.json
python3 CASE/implementation/check.py --project-root ROOT
python3 CASE/implementation/check.py --project-root ROOT --receipt C/verification.json --receipt CPP/verification.json
```

Fresh --build-root NEW must be create-only under model/build; omission uses a UUID. Each mode retains verification.json, object/IR/MD/complete disassembly and logs. Default check reads source/metadata only. Explicit receipts require actual archives, all five project sources plus resource header, exact recipes/tools/artifacts and fail on missing files. Replay neither executes nor recompiles the adapter.

CASE is published analysis/v4160-resident-native-2026-10-22 or workspace apk-analysis/tsl9-v4160-resident-native-2026-10-22. Python/sh entries are portable; this round admits only existing pinned Windows NDK LLVM hashes. SDK candidate addresses/contracts are conditional references, not installed-ROM identity. Full original ABI, provider readiness and physical/OTA proof remain false.
