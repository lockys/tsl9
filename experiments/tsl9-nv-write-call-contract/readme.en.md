# NV write: repair actual quarter-call compiler clobber contracts

[繁體中文](readme.zh-TW.md) · [English](readme.en.md)

This new profile adds only the two measured missing A1 clobbers: FN_CALL_UNLOCK and FN_CALL_ERASE. It ordinarily includes old flash_native.h/native_io.h, keeps the definitions through include guards, overlays those two macros, then includes sealed NV-write C. All algorithms, eight genuine functions and compiler flags remain unchanged. Old sources, seals, objects and images are untouched.

**Actual C11/C++17 compilation and read-only replay pass. All eight functions' raw code, sizes, own-written GPRs and ten relocations exactly match the prior object.** Whole ET_REL remains 394 B / 148 instructions / eight globals, UND=0, RELA=10, no ABS provider. The repair changes the compiler-call declaration; identical code for this profile does not make the previous generic declaration correct.

## Coverage of all five genuine callees

Actual object instructions derive every own-written GPR. Actual LLVM inline-ASM supplies output, input-only and clobber sets:

| Callee | Actual own-written registers | Old missing writes | New declaration |
| --- | --- | --- | --- |
| unlock | A1/A3/A4/A5 | A1 | Fully covered |
| status | A5 | None | Fully covered |
| erase | A0/A1/A3/A4/A5 | A1 | Fully covered |
| program | A0/A2/A3/A4/A5/A6 | None | Fully covered |
| lock | A3/A4/A5 | None | Fully covered |

Every call retains RA link and memory clobbers. Actual program code preserves its input-only A1. Standard C/PSABI labels do not substitute for those checks. The profile reports compiler-call contract repaired=true only when all five callees' actual writes are covered.

Whole LLVM IR comparison ignores only ModuleID, source_filename and !srcloc source-location annotations. Everything else matches except two added ~{x11} clobbers on unlock/erase. All eight functions, including genuine unused status/quarter, remain. There is no fake FUNC, stub, ABS provider or opcode carrier.

Quarter remains 64 B / 23 instructions with a 32-byte frame; write remains 72 B / 26 with a 16-byte frame; timer remains 60 B / 23. This round does not repair timer A1/A2 exits, original write-frame/source-reload differences, fault/IRQ/asynchronous behavior or adverse aliasing. Full original register ABI, installed-provider identity, placement and physical validation stay false.

## Genuine baselines and portable replay

Each baseline folder supplies actual prior native.o and native.ll; **old verification.json is neither read nor replayed**. The object must exactly match the independently read SHA256:

`b30c679bd1e15a7a59be59b4ed723a6f98f78cc022e93e314e4c59f85c7aa09f`

baseline-facts.json retains per-function code hashes, written registers, relocations and language-specific normalized IR hashes from genuine old artifacts. A new build copies actual baseline inputs into mode/baseline/native.o and mode/baseline/native.ll and reads them with real objdump. Replay depends only on the new local archive, without the original baseline folder or old W receipts.

```sh
sh experiments/tsl9-nv-write-call-contract/verify.sh --project-root ROOT --tool-dir LLVM --build-root NEW --baseline-c-folder OLD_C --baseline-cpp-folder OLD_CPP
python3 CASE/implementation/check.py --project-root ROOT
python3 CASE/implementation/probe.py --project-root ROOT --replay MODE/verification.json
python3 CASE/implementation/check.py --project-root ROOT --receipt C/verification.json --receipt CPP/verification.json
```

CASE supports workspace apk-analysis/tsl9-v4160-nv-call-contract-2026-10-22 and delivered analysis/v4160-nv-call-contract-2026-10-22. NEW is create-only beneath model/build; omission uses UUID. W defaults to the current root's old model/build/native-v1/{c,cpp}; D/P should supply validated actual baseline folders. Current W outputs are build/contract-v1/{c,cpp}.

New receipts retain mode/source_pins/tools/artifacts/commands, seven complete MD inputs, IR, full disassembly of both objects, actual tool/resource hashes and all raw logs. Default check reads source/metadata only; explicit receipts inspect real object/IR without compilation or execution. Static classifiers retain two verified legacy files and their relative import hierarchy; delivered canonical paths are analysis/function-hardware/fifty-fifth-round and fifty-seventh-round.

One source overlay/compiler recipe is used, without flag search or failed-compilation retries. No native/CPU/ISA/ESIL/MMIO/HOST/hardware/vendor/network operation, link or BIN occurs. Authored text uses LF and one EOF newline; default README equals Traditional Chinese, with English separate. The previously denied Git Bash is not retried; sh runtime remains unverified.
