# TSL9 offline C/C++ reconstruction

[繁體中文](README.md) | [简体中文](readme.zh-CN.md)

This project preserves the original APK, 22 distinct updater BINs, readable C/C++ behavior models and static source evidence. The goal remains a rebuilt BIN compatible with the original hardware and BLE updater, while identifying worthwhile new features during reverse engineering and keeping proposals separate from implemented functions. **No rebuilt BIN is currently verified as flashable.**

## Portable verification

The latest complete image integrates the OTA page reply: twelve readable IRQ/Flash/OTA functions total 650 bytes, and the complete 76,800-byte BIN matches official ID2966 V4.1.60. Each C/C++ pipeline freshly compiles 43 translation units, records complete header dependencies and runs 61 commands including two explicit ABI ordering stages. The remaining 679 sections still use original carriers. This is partial source recovery, **not hardware or BLE OTA validation**. See the [new integration](analysis/v4160-reply-image-integration-2026-10-22/readme.en.md) and [offline image](artifacts/offline-images/ID2966-V4.1.60-reply-integrated/readme.en.md).

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
| Reset data-copy, BSS clear and output registers | [English guide](experiments/tsl9-v4160-reset-memory/readme.en.md) |
| Interrupt initialization normal register contracts | [English guide](experiments/tsl9-v4160-interrupt-registers/readme.en.md) |
| Original-address RCC byte identity and new IRQ core | [English guide](experiments/tsl9-v4160-irq-native/readme.en.md) |
| 144-byte IRQ callframe fitting its original extent | [English guide](experiments/tsl9-v4160-irq-callframe/readme.en.md) |
| Readable IRQ source integrated into the complete original layout | [English guide](analysis/v4160-irq-image-integration-2026-10-21/readme.en.md) |
| Six readable Flash functions and original-address components | [English guide](analysis/v4160-flash-native-2026-10-22/readme.en.md) |
| Natural 100-byte program and original entry order | [English guide](analysis/v4160-flash-entry-order-2026-10-22/readme.en.md) |
| Complete offline image with eleven IRQ/Flash functions (flashability unverified) | [English guide](analysis/v4160-flash-image-integration-2026-10-22/readme.en.md) |
| Five Flash leaves with matching register/instruction prefixes | [English guide](experiments/tsl9-v4160-flash-register-prefix/readme.en.md) |
| Explicit ABI stack-save scheduling and read-only replay | [English guide](experiments/tsl9-v4160-frame-schedule/readme.en.md) |
| Complete offline image with eleven readable functions matching official bytes | [English guide](analysis/v4160-register-image-integration-2026-10-22/readme.en.md) |
| Feature candidates and existing-feature evidence | [English proposals](analysis/v4160-irq-callframe-2026-10-21/feature-candidates/readme.en.md) |
| Runtime main/init/loop/dispatch | [Guide](experiments/tsl9-v4160-runtime-loop/readme.en.md) |
| Reference resident entry and byte-copy | [Entry](experiments/tsl9-resident-entry-reference/readme.en.md) / [copy](experiments/tsl9-resident-copy-reference/readme.en.md) |
| Published file identity | [Manifest](publication-manifest.json) |

WCH CH32V20x, including CH32V208 as a subfamily candidate, is retained as a hardware hypothesis. Register-map and code similarities do not identify an exact TSL9 part, board, installed ROM, pinout or interrupt ABI. The captured resident candidate remains incomplete; synthetic continuation does not fill its missing original bytes.

The existing 76,800-byte source-identical offline image remains **NOT-FLASH-VALIDATED**. No BLE/UART/CAN or physical Flash I/O is part of these tests. Commit/push follows each verified milestone. `README.md` displays Traditional Chinese by default; English and Simplified Chinese live in `readme.en.md` and `readme.zh-CN.md`, with a separate Traditional Chinese copy in `readme.zh-TW.md`. Languages are maintained separately and historical sealed documents retain their original contents. Real device identifiers, credentials, private request/response logs and temporary builds are excluded from publication.
