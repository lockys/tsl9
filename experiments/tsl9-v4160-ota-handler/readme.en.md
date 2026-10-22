# Readable V4.1.60 OTA handler C/C++

[繁體中文](readme.zh-TW.md)

Shared C11/C++17 reconstructs U/S/W/R/E at `0x9C4A..0x9E5C`. The original is 530 bytes /169 instructions. Actual native compilation produces 776 bytes /285 instructions with a 112-byte frame. Original placement and complete ABI remain unproved. No link, BIN export, RISC-V execution or hardware OTA test occurred.

W preserves fresh GP state, BE16 page, the original unsigned range expression, offset increment before quarter calls, and Flash-word-before-source-word readback. Its nominal destination is BOOT alias `0x08001000 + page*1024`, not Runtime self-flashing. R does not inherit W's page guard. UID success is raw zero; U/S retain `(length-1)&255` and S's pre-call stack bytes versus post-call live S1.

The HOST API models named algorithm state and synthetic effects, not a CPU. Only opaque call providers may change named state/args; memory providers may change synthetic memory. Defined argument masks are selected projections, not complete physical raw8 proof. W reply additionally carries A3=last source word, A4=1024 and A5=mismatch offset. No common success result is invented. Diagnostic budgets are HOST boundaries, never native timeouts.

Formal HOST results per language: 10 cases /8292 checks and three actually compiled semantic negatives. Independent results: 16 narratives /18 dispatches /898 checks and four compiled negatives. These do not establish physical ABI or hardware behavior.

```sh
python3 -B experiments/tsl9-v4160-ota-handler/verify_host.py --project-root . --language both
sh experiments/tsl9-v4160-ota-handler/verify.sh --project-root . --language both
python3 -B experiments/tsl9-v4160-ota-handler/verify_host.py --project-root . --replay PATH/verification.json
python3 -B apk-analysis/tsl9-v4160-ota-handler-2026-10-22/implementation/verify_native.py --project-root . --tool-dir /path/to/llvm/bin --language both
```

Published case paths use `analysis/v4160-ota-handler-2026-10-22`; the working tree uses `apk-analysis`. Native `--replay RECEIPT` performs read-only artifact checks. Fresh output uses a create-only UUID directory under this model's `build/`; an explicit `--build-root` must also be new and inside it.

Native retains nine true undefined symbols and 23 relocations without numeric ABS providers, stubs or libc substitutes. Four exact recipes bind sources/tools before and after use, actual three-project-file plus Clang `stdint.h` MD closure, all artifacts and complete instruction bytes. Conventional callee S/SP preservation remains conditional; mutable HOST named state does not prove native physical preservation. The original BIN is never a code-generation input.

Every HOST launch uses the immutable machine guard; replay reparses executable identities. Windows HOST was tested. Portable interfaces do not claim live Linux/macOS results. The guard supports thin Mach-O Python, not universal/fat Python.

Publish only source/docs/selected receipt metadata and seals. Build logs, executables, objects and IR stay local. Historical `probe.py` measured an earlier 752-byte draft and is not the formal producer. The 246-byte size gap, frame/register contracts and real-provider integration remain open.
