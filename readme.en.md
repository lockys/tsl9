# TSL9 offline C/C++ reconstruction

[繁體中文](README.md) | [简体中文](readme.zh-CN.md)

This project preserves the original APK, 22 distinct updater BINs, readable C/C++ behavior models and static source evidence. The goal remains a rebuilt BIN compatible with the original hardware and BLE updater, while identifying worthwhile new features during reverse engineering and keeping proposals separate from implemented functions. **No rebuilt BIN is currently verified as flashable.**

## OTA commands rebuilt as shared C/C++

Readable C11/C++17 now covers U/S/W/R/E commands, preserving UID, length, page, live mode, four quarter writes and word-by-word readback order. Both languages pass the own and independent HOST suites. Actual native objects each contain **776 bytes / 285 instructions / a 112-byte frame**, exceeding the original 530-byte region by 246 bytes, with nine true undefined references. **No link or BIN integration; the complete TX image is unchanged.** W writes a BOOT alias and does not prove Runtime self-update. [Code, evidence and gaps](./analysis/v4160-ota-handler-2026-10-22/readme.en.md)

## Callback native component reduced to 624 bytes

New C11/C++17 components each contain 624 bytes / 223 instructions. They explicitly reserve S10/S11, read the current physical GP at six uses and swap two existing saves through an explicit stage. Independent reviews confirm a 48-byte frame, eleven save/restore pairs and fifteen indirect calls; HOST suites are not rerun. The remaining eight original bytes contain executable instructions. Full prefix, call-return ABI, tail ownership and original placement remain unproved. **This component is not integrated and adds no BIN; the existing complete TX image is unchanged.** [Evidence and limits](./analysis/v4160-callback-registers-2026-10-22/readme.en.md)

Further static call-boundary review confirms that the GP+42 datum is killed before both calls, with no missing A4 argument here. The small function pair behind `+0x13C` in two official ROM candidates only saves/returns through RA and does not observe incoming S4/S7. This narrows specific constraints, without identifying installed ROM or proving other callees. Candidate slots correspond to CCC configuration reads and notification submission; the read returns 0..255, so the original `==1` and `&1` gates remain distinct. [Call boundaries and candidate conditions](./analysis/v4160-callback-call-frontiers-2026-10-22/readme.en.md)

## Previous readable event callback and native gaps

The 632-byte callback at `0x8614..0x888C` now has readable C/C++ covering event priority, two context/connection records, chunk length, retries and follow-up events. A single explicit-inline diagnostic reduces native allocation from 1,034 to one 658-byte function with a 48-byte frame and fifteen indirect calls. It remains 26 bytes too large, with extra S10 saves, save order, return-address and unknown-ROM contracts unresolved. **This callback is not integrated into the complete BIN and adds no flashable image.** [Analysis and limits](analysis/v4160-event-callback-2026-10-22/readme.en.md)

## TX source in a complete experimental BIN

Fresh C11/C++17 pipelines each compile 46 units and produce the same 76,800-byte experimental BIN. Thirteen original function regions / 930 bytes use fifteen real FUNC roles; 678 other sections retain original carriers. All 93 differences from official ID2966 are inside TX; other bytes are unchanged. SHA-256: `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`. **The new BIN is not verified as flashable.** [Complete integration](analysis/v4160-tx-image-integration-2026-10-22/readme.en.md) | [Experimental image](artifacts/offline-images/ID2966-V4.1.60-tx-integrated/readme.en.md)

## Portable verification

OTA transmit entry `0x8A56` now has an actual 280-byte native component: an eight-byte narrow assembly entry, a 270-byte readable C/C++ body and a two-byte return leaf. Oversized input returns without touching the stack, and both resident-call return addresses match. A separate new scheduling stage checks saved-register ordering. **This component is now integrated above, with original hardware and BLE OTA still unvalidated.** See the [entry/frame analysis](analysis/v4160-tx-register-abi-2026-10-22/readme.en.md), [original TX contract](analysis/v4160-ota-tx-2026-10-22/readme.en.md) and [feature proposals](analysis/v4160-ota-tx-2026-10-22/continuation-plan/readme.en.md).

The previous complete image integrates the OTA page reply: twelve readable IRQ/Flash/OTA functions total 650 bytes, and the complete 76,800-byte BIN matches official ID2966 V4.1.60. Each C/C++ pipeline freshly compiles 43 translation units, records complete header dependencies and runs 61 commands including two explicit ABI ordering stages. The remaining 679 sections still use original carriers. This is partial source recovery, **not hardware or BLE OTA validation**. See the [new integration](analysis/v4160-reply-image-integration-2026-10-22/readme.en.md) and [offline image](artifacts/offline-images/ID2966-V4.1.60-reply-integrated/readme.en.md).

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
