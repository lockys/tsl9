# Partial linking against real providers

[繁體中文](readme.zh-TW.md)

One standard `ld.lld --no-relax -r` invocation combines two existing objects verified against their retained generation receipt artifact maps. No C/C++ or HOST compilation occurs. Actual C and C++ cases each measure:

| Fact | Base carrier | Compact native | New ET_REL |
|---|---:|---:|---:|
| Nonempty allocated sections | 691 | 1 | 692 |
| RELA | 8261 | 20 | 8281 |
| True UND | ROMentry 1 | 9 | ROMentry 1 |

All nine native UND bind to real allocated baseline providers, retaining section-relative values/sizes/info/visibility. `__tsl9v4160_rom_entry` remains genuinely undefined. No ABS/defsym/stub/undefined-ignore/fake-size providers are introduced.

Original raw530 owner with its NOTYPE0 entry and separate truthful new FUNC568 coexist. Existing callers still target the original handler; no entry reroute occurs. Every original allocated byte and NOBITS/type/flags/alignment/size role survives, native568 bytes stay unchanged, and the complete relocation multiset is the two-input union with only the nine real provider-role resolutions.

This establishes provider closure, not a functional full image. Relocations remain in ET_REL; JAL application/range checking is not claimed. Actual native instruction bytes are unchanged. No final ELF/BIN, placement, installed ABI, OTA or RISC-V execution is established.

```sh
python3 -B apk-analysis/tsl9-v4160-ota-handler-layout-2026-10-22/provider-link/link.py \
  --project-root . \
  --base-object PATH/c/source-integrated.o --base-receipt PATH/c/verification.json \
  --native-object OTHER/c/ota_handler.o --native-receipt OTHER/c/verification.json \
  --ld /path/to/llvm/bin/ld.lld --build-root NEW-OWNED-DIR
```

Language mode is inferred from matching input receipts. Only the exact retained TX-integrated base C/CPP hashes and sealed compact568 native hash are supported. The linker must match the pinned Windows NDK identity (ld.lld.exe on Windows); other binary versions/platforms were not tested. Portable Python/shell metadata interfaces do not establish native Linux/macOS linker support.

Fresh output is a new UUID directory under this scope/build. Explicit --build-root must also be new and inside it. Outputs are PROVIDER-CLOSURE-ONLY.o, log and verification.json. Stdout identifies receipt/hash/mode, nine bindings and remaining UND. Explicit object/receipt paths avoid hidden W dependencies. Inputs/receipts/linker/runner/parser identities are checked before and after use.

```sh
python3 -B apk-analysis/tsl9-v4160-ota-handler-layout-2026-10-22/provider-link/link.py --project-root . --replay PATH/verification.json
python3 -B apk-analysis/tsl9-v4160-ota-handler-layout-2026-10-22/provider-link/check.py --project-root .
python3 -B apk-analysis/tsl9-v4160-ota-handler-layout-2026-10-22/provider-link/check.py --project-root . --receipt PATH/verification.json
```

Published paths use analysis/v4160-ota-handler-layout-2026-10-22. Default checking verifies seal/source dependencies/selected metadata only with actual flags false. Explicit --receipt reads actual input/output objects, receipts, command/log and complete output inventory. Replay launches no linker. Opaque objects/build archives are excluded from source-only publication; metadata-only checking without them is not actual replay.
