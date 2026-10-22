# OTA reply: an independent four-byte C object

[繁體中文](readme.zh-TW.md)

Actual C11/C++17 output is **550 bytes / 186 instructions / a 48-byte frame**. A genuine aligned four-byte volatile C object occupies SP+12..15. Its first two bytes carry the reply; its pointer is entry SP-36, matching the original selected address. The lowest saved word is S6 at SP+16, so the entire object avoids saved storage.

| Actual artifact | bytes / instructions | saved words | first two reply bytes |
| --- | --- | --- | --- |
| Prior sealed version | 556 / 188 | 9 | SP+10,11 |
| Full Flash base formed before copy | 552 / 186 | 8 | SP+14,15 |
| Four-byte reply backing | 550 / 186 | 8 | SP+12,13 |

Only two source profiles were compiled. First, an identity native +r port after the range guard forms the full Flash base before the optional copy call, eliminating a split constant carried across that call. Second, standard C11 `_Alignas(4)` / C++ `alignas(4)` declares a four-byte reply array. No compiler flags, extra initialization or four-byte transmission were added. The shared algorithm, effect order, all eight register read/write operands and memory clobbers remain. HOST uses identity and excludes the native declaration; unchanged HOST suites were not rerun.

This closes only independent object ownership and the selected numeric reply address. The original body is 530 bytes; this one is still 20 bytes larger and additionally saves S6. Save order, call RA values, opaque S/GP/SP observations and callback lifetime are not fully proved. Full original ABI, placement, installed ROM/BOOT and OTA admission remain false. The live model and BIN remain unchanged. No link/BIN, target/ISA execution or hardware operations occurred.

## Reproduce

```sh
sh experiments/tsl9-v4160-ota-reply-object/verify.sh --project-root "$PWD" --tool-dir /path/to/llvm/bin --language both
```

Outputs are create-only under model/build; omission of build-root creates a UUID directory. Each mode retains the object, IR, complete disassembly, -MD, logs and verification.json. Nine genuine undefined symbols and twenty relocations remain unresolved without numeric providers.

The case implementation/probe.py supports `--project-root ROOT --replay MODE/verification.json`. check.py defaults to metadata only. Repeated explicit `--receipt` arguments read actual recipes, sources, tools, resource header, dependencies, artifacts and reply storage. Published case path: analysis/v4160-config-lifetime-2026-10-22; workspace path: apk-analysis/tsl9-v4160-config-lifetime-2026-10-22.

Python/sh entry points are portable; this round measures pinned Windows LLVM binaries and does not admit unverified Linux/macOS tools. The historical 552-byte source snapshot and receipts remain under build/full-base-v1; they cannot be replayed as current-source identity with the later four-byte source. Only source and metadata are published, without opaque objects. No original BIN bytes are code-generation input.
