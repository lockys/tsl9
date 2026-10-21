# TSL9 offline C/C++ reconstruction

This project preserves the original APK, 22 distinct updater BINs, readable C/C++ behavior models and static source evidence. The goal remains a rebuilt BIN compatible with the original hardware and BLE updater. **No rebuilt BIN is currently verified as flashable.**

## Portable verification

Requirements: Python 3.10+, a C11/C++17 compiler, and a POSIX shell. Linux can use GCC or Clang, macOS can use Clang, and Windows can use Git Bash plus Visual Studio C++ Build Tools. PowerShell and CMake are not required by the portable entry.

```sh
sh ./verify.sh --list
sh ./verify.sh --model runtime-loop --language both
sh ./verify.sh --model system-clock-query --language both
```

Run `sh ./verify.sh` for all currently registered portable models. The same backend can be called directly with `python scripts/portable_verify.py`. Set `CC`/`CXX` to a single compiler executable, or `PYTHON` to a Python executable for the shell entry. Paths are resolved from the checkout, not the caller's working directory. Build outputs go into fresh ignored directories.

The initial portable registry covers runtime-loop, system-clock-query, resident-entry and resident-copy. Each entry checks its exact original artifacts, sealed raw source proof, source dependencies and C/C++ host behavior. Receipts include actual compiler/executable hashes. Original firmware is read as data and is never executed or emulated.

The repository also contains 116 historical PowerShell scripts. Their native RV32, ELF, integration and download checks require individual migration; a host-test pass does not replace those checks. Historical sealed files retain their original bytes. See the migration inventory for precise scope. Cross-platform CI results are reported separately from local tests and hardware evidence.

## Contents

| Content | Location |
| --- | --- |
| Original APK 1.2.7 | [APK](artifacts/apk/安卓-TSL电子模块-1.2.7-1.apk) |
| 22 original decoded BINs | [Firmware archive](firmware-downloads/legacy-options-2026-10-20/BINs/) |
| New clock calculation model | [English guide](experiments/tsl9-v4160-system-clock-query/readme.en.md) |
| Readable native interrupt initialization | [English guide](experiments/tsl9-v4160-interrupt-init/readme.en.md) |
| Readable native clock and derived fields | [English guide](experiments/tsl9-v4160-native-clock/readme.en.md) |
| Clock normal-return register contracts | [English guide](experiments/tsl9-v4160-clock-registers/readme.en.md) |
| Runtime main/init/loop/dispatch | [Guide](experiments/tsl9-v4160-runtime-loop/readme.en.md) |
| Reference resident entry and byte-copy | [Entry](experiments/tsl9-resident-entry-reference/readme.en.md) / [copy](experiments/tsl9-resident-copy-reference/readme.en.md) |
| Published file identity | [Manifest](publication-manifest.json) |

WCH CH32V20x, including CH32V208 as a subfamily candidate, is retained as a hardware hypothesis. Register-map and code similarities do not identify an exact TSL9 part, board, installed ROM, pinout or interrupt ABI. The captured resident candidate remains incomplete; synthetic continuation does not fill its missing original bytes.

The existing 76,800-byte source-identical offline image remains **NOT-FLASH-VALIDATED**. No BLE/UART/CAN or physical Flash I/O is part of these tests. Commit/push follows each verified milestone. New documents use separate `.en.md` and `.zh-TW.md` files; `README.md` is a language index. Real device identifiers, credentials, private request/response logs and temporary builds are excluded from publication.
