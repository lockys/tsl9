# TSL9 offline C/C++ reconstruction

[繁體中文](README.md) | [简体中文](readme.zh-CN.md)

This project preserves the original APK, 22 distinct updater BINs, readable C/C++ behavior models and static source evidence. The goal remains a rebuilt BIN compatible with the original hardware and BLE updater, while identifying worthwhile new features during reverse engineering and keeping proposals separate from implemented functions. **No rebuilt BIN is currently verified as flashable.**

## NV write callback and timer reconstructed in C/C++

The write entry is72B/26 instructions and timer60B/23 instructions; six genuine Flash helpers bring the complete object to eight functions,394B/148 instructions. C11/C++17 bytes match. Actual linking resolves all ten calls to genuine C definitions in the offline component, with independent ELF review. Original-source294B/115rows, calibration-relation44B/12rows and12 native controls per language were also checked.

**No new firmware BIN or integration into the existing candidate.** Frame/output registers differ, and the old quarter asm-call declaration omits two A1 clobbers. Full ABI, fault/IRQ, installed ROM/memory and BLE OTA remain unproved. Offline calibration diagnostics are a feature proposal. [C/C++, component and full limits](analysis/v4160-nv-write-2026-10-22/readme.en.md)

## NV-read callback reconstructed; normal-exit scratch checked

The original 30-byte NV-read callback is reconstructed as real C11/C++17: 32 bytes / 14 instructions, one global FUNC, UND0/RELA0/ABS0. Independent inspection checks the fresh slot, word-count shift, indirect-call arguments and zero return, rejecting eight controls per language. Extra A3, fault ordering and original extent fit remain limitations. **No new BIN; the function is not integrated into the existing candidate.**

The ADC scratch word is overwritten with the same `0x198EA` at normal callback exit; this does not guarantee infinite polling returns or prove all-RAM/IRQ equivalence. Config+56/+60 now connect to original App read/write functions. The conditional numeric NV range is `0x08077C00..0x08077F00`; original hardware Flash ownership and OTA remain unproved. [C/C++, source and all limitations](analysis/v4160-callback-frontiers-2026-10-22/readme.en.md)

## ADC caller linked to a real C/C++ experimental image

A register allocation derived from the original caller produces identical C11/C++17 functions of 110 bytes / 42 instructions, preserving A7 and T/S/GP/TP while adding a 16-byte private frame. Independent review supports the normal caller projection under explicit premises; private frame residue is outside that observation. Full original ABI, fault and interrupt equivalence remain unproved.

An actual assembler JAL relocation and linker connect the function in a separate **78,848-byte offline candidate**, preserving the previous 77,824-byte image. Only three original caller bytes change; an appended page contains 110 bytes of C code and 914 bytes of explicit FF packaging data. Independent readers inspect ELF, LOADs, JAL and the entire BIN; linker GC removes four unused real functions. **The candidate remains NOT-FLASH-VALIDATED; original-hardware OTA compatibility is unproved.**

Two candidate resident libraries each contribute 8 complete functions (1,056 bytes / 359 rows). Indirect callbacks at config+52, config+56 and fresh live S0+60 remain open, as do installed ROM, BOOT and Flash/NV/RAM ownership. Offline compatibility and configuration diagnostics are proposals. [C/C++, actual artifacts and source evidence](analysis/v4160-adc-caller-2026-10-22/readme.en.md)

## ADC configuration reconstructed in C/C++; callback dependencies closed

Shared C11/C++17 reconstructs the original88B/37-instruction configuration logic with14 ordered IO effects, complete high bits, alias feedback and uint32 wrap. Producer HOST has80cases/6864checks per language; independent HOST has74cases/2904checks; each suite rejects3actual compiled semantic controls per language. Native entry102B/38instructions has no call/frame; the whole254B/93-instruction object has5genuine global FUNC and UND0/RELA0. **Extra A2/A6/A7 writes and14-byte oversize remain unresolved; no newly rebuilt firmware BIN.**

Eight original functions cover386B/148rows, closing restricted dependencies at all13 call sites of the364-byte callback. Normal SP/RA/S/GP/TP preservation requires a valid disjoint144-byte stack and other explicit premises. Polling has no timeout or guaranteed termination. This caller overwrites A2/A6 later; original A7 survives to exit, so the new A7 write still escapes. The normal reading is raw16, not calibrated Celsius. [C/C++, tests and original source](analysis/v4160-adc-config-2026-10-22/readme.en.md)

## Complete fixed-register recipe still fails the original ABI

One complete source-derived bank per leaf compiled successfully in six actual C11/C++17 objects. Selected compare60/fill68/copy64 bytes (23/24/22 instructions) all add16-byte frames and RA/SP writes; fill also temporarily writes A2. This recipe cannot directly replace the original leaves. Whole objects retain eleven genuine global FUNC definitions each, allocating454/492/418B, UND0/RELA0. **No new BIN; existing components and experimental image remain unchanged.**

Original0x188E2 and its sole dependency0x19160 cover106B/37 rows. Callback input0x40012400 selects mask0x200: OR, then a fresh read and AND ~mask, not whole-word restoration. The bounded chain preserves SP/RA/S/GP/TP under explicit premises; whole callback/config52 lifetime remains unproved. Next gap:0x19896→0x1892E. [C/C++, independent ABI and source evidence](analysis/v4160-register-contract-2026-10-22/readme.en.md)

## Native memory IO entries without context or stack frames

Sealed shared C algorithms now have real volatile byte/word IO and FENCE.I. After two measured profiles, C11/C++17 three-u32/u32-result entries are compare52/fill48/copy52 bytes, totaling152B/52 instructions. These three entries have no context/sret, call or explicit SP/RA/S/A1/A2 write. Eight genuine unused global functions remain (230B); the whole object is382B/138 instructions, UND0/RELA0. **Extra registers, scratch residues and fault timing still differ; fill exceeds its original extent by2B. Full ABI/placement remain unproved; no new BIN.**

The original App field44 entry197F0 has a364B/130-instruction source range. An aligned zero-fill path and two small RCC leaves narrow early effects, but13 call sites and a polling loop without an encoded timeout retain unresolved dependencies. No callback-wide staCB-zero guarantee is claimed. [Native C/C++, artifacts and limits](analysis/v4160-resident-native-2026-10-22/readme.en.md)

## Three conditional resident memory leaves reconstructed in C/C++

New C11/C++17 components implement compare-byte, fill and forward copy, retaining the MMIO guard/FENCE.I before argument checks and restoration on normal completion. Compare uses the full32-bit expected value; fill returns the advanced address, while copy returns the original destination and retains forward-overlap feedback. Synthetic IO tests and native-object inspection validate the authored components; **they are not installed-ROM providers and produce no new BIN**.

Both complete228-byte/92-instruction initializers were read. Under explicit mapping, valid-memory, no adverse alias/asynchronous modification and normal-return premises, the staCB-zero deduction extends through config copy to the first subsequent callback entry. Its original App numeric source is197F0; the tsCB/temperature name is a header inference. Its effects and later initialization remain unresolved. [C/C++, evidence and limits](analysis/v4160-resident-memory-2026-10-22/readme.en.md)

## A 550-byte C/C++ component now owns storage at the original reply position

The new C11/C++17 component has **550 bytes /186 instructions /48-byte frame**. A genuine4-byte object occupiesSP+12..15, with only its first two bytes written and no overlap with saves startingSP+16. Given the same entrySP, its reply pointer matches originalSP−36. Correlated S-length2 and empty-E0/0 edges are independently checked. **Only the storage/pointer projection closes: extraS6 saves, full callee/IRQ ABI, placement and OTA remain unproved. The existing568 component/BIN is unchanged.**

Bounded reads also cover a50-byte MAC helper and two46-byte candidate fill leaves. Under explicit valid-stack/normal-access/no-alias/no-async premises, App staCB is zero at BLE-init call entry. This does not extend inside the callee or through callback lifetime. [Code, actual evidence and conditions](analysis/v4160-config-lifetime-2026-10-22/readme.en.md)

## Allocator callback field origin and a 556-byte C/C++ experiment

Actual64-byte initialization copies in two candidates trace the allocator callback word to config `staCB` (+52). Actual RV32 C compilation verifies both header layouts. The original App sets numerical SNV address `0x08077C00`, without proving other Flash free. Two motivated C lifetime changes reduce the OTA component to **556 bytes /188 instructions /48-byte frame**, removing one S8 save/restore pair. Its independent reply object is SP+10/11, still2 bytes below original SP+12/13. **Pointer ABI remains unproved; the existing568-byte component and complete BIN are not replaced.** [Code, actual evidence and limits](analysis/v4160-allocator-callback-2026-10-22/readme.en.md)

## The original OTA caller now reaches real C/C++ in a complete experimental image

A genuine same-TU strong alias connects the original caller to new C11/C++17. The actual JAL at `0x14094` reaches `0x1AC00`, retaining return address `0x14098`. Both languages produce the same **77,824-byte** experimental BIN. Only three bytes of that instruction change within the inherited 76,800 bytes; the original530-byte handler remains, followed by new568-byte C and456-byte non-executable FF page packaging. SHA-256: `3be918942c03de99c8a5f3fb7d6eba40ab9af63930020efb7f4cac07cc9a10ee`.

**This BIN is not verified as flashable.** The partial link retains a true ROM undefined symbol. The complete ELF only reuses the historical numerical `0x40000` boundary corroborated by the original JAL at `0x18730`; this supplies neither a ROM implementation nor installed identity. Added Flash/NV ownership, callee/stack ABI, physical BOOT and OTA acceptance/recovery remain unproved. Both candidate allocator paths forward ambient A2 to another unknown callback, so reply addresses cannot be declared unobserved. [Code and evidence](analysis/v4160-ota-source-wiring-2026-10-22/readme.en.md) | [Experimental image](artifacts/offline-images/ID2966-V4.1.60-ota-source-wired/readme.en.md)

Historical statements below about no integration/new BIN retain their original milestone scope.

## Nine OTA providers bound in actual partial links

Real `ld.lld -r` links bind all nine external references of the existing568-byte C/C++ component to allocated providers; only the original ROM entry remains undefined. **The original caller is not redirected to new C; no final ELF or new BIN.** Reply-pointer escape into allocator-slot A2 remains an ABI obligation. Candidate BOOT allows Runtime pages through95; numeric headroom is not free Flash. [Tools, raw evidence and placement limits](./analysis/v4160-ota-handler-layout-2026-10-22/readme.en.md)

## OTA native component reduced to 568 bytes

Separating reply-array lifetime and sharing three C terminal reply sites reduces the component from 776 bytes / 285 instructions / a 112-byte frame to **568 bytes / 193 instructions / a 48-byte frame**, preserving the eight-register call bridge and command effects. It still exceeds the original530-byte region by38 bytes. **No link or new BIN; the complete TX image is unchanged.** An explicit erratum corrects the previous analysis README claim of four unrolled quarter callsites: actual objects have one loop callsite. [Code, independent review and limits](./analysis/v4160-ota-handler-compact-2026-10-22/readme.en.md)

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
