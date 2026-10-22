# NV-read callback: C/C++ reconstruction of a conditional indirect call

[繁體中文](readme.zh-TW.md) · [English](readme.en.md)

Actual ID2966 V4.1.60 firmware was read and the existing finite decoder re-decoded **30B / 13 rows at 0x1979A..0x197B8** before readable C11/C++17 reconstruction. This round compiles and statically reads artifacts only. No callback/native code, CPU/ISA, MMIO, hardware or network operation executes; no previous HOST matrix is rerun.

Public `tsl9_nv_read_callback_1979a(source,words,destination)` is a conditional three-u32 physical-register surface, not a recovered original C prototype. Each invocation freshly reads volatile slot **0x4004C** and makes a genuine indirect call through that loaded value:

```text
callee A0 = entry A2 (destination)
callee A1 = entry A0 (source)
callee A2 = uint32(entry A1 << 2) (byte count)
normal callback A0 = 0, ignoring the callee's normal A0 result
```

The function pointer's three-u32 inputs/u32 normal result are conditional on the slot implementing the sealed copy candidate's observed register/effect projection. Original prototype, installed slot→copy identity and full callee ABI remain unproved. SDK names are not evidence. The loaded value is not replaced with a constant candidate address; no fallback, stub or fake provider exists. Unsigned count shifting preserves 32-bit wrap. Failure to return normally does not fabricate callback result 0 or cleanup.

## Actual native results

| Item | Original source | New C and C++ |
| --- | ---: | ---: |
| Function bytes / instructions | 30 / 13 | 32 / 14 |
| Genuine global FUNC | Raw source range | One; no unused global |
| Frame | 16B | 16B |
| Own-written GPRs | RA/SP/A0/A1/A2/A4/A5 | Adds A3 |
| UND / RELA / ABS provider | Non-ELF input | 0 / 0 / 0 |

Both languages produce identical function bytes, SHA256 `be3e03eacb688e38d8dbebdd509b900520385a2a2084136c4bdbfdd5f5caad3c`. The real call is JALR RA,A5. Full finite raw operand decoding and LLVM disassembly are retained. Zero UND does not establish a known or verified dynamic slot target.

The original loads the slot before frame allocation/RA save. New code subtracts 16 from SP and saves RA at entrySP-4 before loading the slot, changing the stack/RA prefix before a possible slot fault. New code sets A0=0 before restoring RA; the original restores RA first, another retained fault-prefix difference.

New A3 temporarily holds entry source; the original wrapper does not write A3 itself. If the actual copy candidate leaves A3 unchanged on a no-loop path, this difference can survive callback return. Caller-saved registers are not assumed freely disposable, nor are A7/T bank or ambient A1/A2 treated as irrelevant. Standard C call syntax alone does not prove original callee/caller ABI.

Actual IR contains one fresh volatile slot load, shl i32 words,2, an indirect call with destination/source/scaled-count, then ret i32 0. That bounded call-boundary projection is not complete fault/IRQ/asynchronous or caller equivalence. Full ABI, placement, installed-provider and hardware proof remain false.

## Running and evidence

```sh
sh experiments/tsl9-nv-read-callback/verify.sh --project-root "$PWD" --tool-dir LLVM --build-root NEW
python3 CASE/implementation/check.py --project-root ROOT
python3 CASE/implementation/probe.py --project-root ROOT --replay MODE/verification.json
python3 CASE/implementation/check.py --project-root ROOT --receipt C/verification.json --receipt CPP/verification.json
python3 CASE/implementation/provenance.py --project-root ROOT --firmware ORIGINAL_V4160.bin
```

CASE supports workspace apk-analysis/tsl9-v4160-callback-frontiers-2026-10-22 and delivered analysis/v4160-callback-frontiers-2026-10-22. NEW is create-only beneath model/build; omission uses UUID. Current W archives are build/verified-v1/{c,cpp}, preserving object, complete IR/disassembly, three actual MD inputs, actual tools/resource stdint.h hashes, raw logs, source pins and receipts. Default check reads source/metadata only. Explicit receipts reread real artifacts without recompiling or executing. Only provenance or check --firmware rereads original firmware and performs finite static decoding.

The existing fixed NDK/-Oz/rv32imac_zicsr_zifencei recipe is unchanged; no register bank, flag sweep or handcrafted opcode is added. No link, BIN or flashing occurs. original-1979a-197b8.bin is only a retained 30B original-evidence slice, not rebuilt firmware. Python/sh sources are portable; native results admit existing Windows NDK hashes only. The previous Git Bash launch denial is not retried, so sh runtime remains unverified. Authored text uses LF, exactly one EOF newline and Git-style whitespace checks; raw compiler logs retain actual bytes.

Initial build/native-v1 C compilation/replay passed; C++ compilation also passed, but the probe rejected its legitimate call noundef i32 return attribute. Only that IR parser representation was repaired; identical sources/flags rebuilt verified-v1 and both formal replays pass. Initial raw artifacts and initial-probe-snapshot.py remain historical, not current-probe replay evidence.
