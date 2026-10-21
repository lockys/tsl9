# Verified milestones

## Placement audit and interrupt register model

The exact owned pool is eight separated original ranges totaling 540 bytes: reset memory 62, clock query 174, fields 40, IRQ initializer **144**, and four RCC helpers **30 each**. A byte-bound audit verifies all 691 section bindings and 8,280 RELA records against the full fixed linker layout. The helpers have other callers. No external direct interior entry was found within admitted code, but 939 indirect instructions leave computed targets unresolved. Summing bytes does not establish a safe contiguous placement.

Actual old native IRQ bodies disprove a useful-looking space assumption: the 118-byte initializer and 22-byte helpers write A2/A3, while the original preserves them. Their A1/A4/A5 residues also differ. A3 survives along the existing caller path to an unresolved callback, so these old bodies cannot supply replacement space under the original contract.

The new `interrupt-registers` C/C++ model retains the 20 MMIO/CSR effects, exact helper A1 bits, branch-specific A4/A5 and final initializer A1=0/A4=128/A5=`0xE000E000`. Each full-source host language passes four groups / 9,184 cases / 246,384 checks. These are host normal-boundary results. Its intended native profile currently fails with `Stack pointer required, but has been reserved.` in all five functions; it emits no object/ELF and has **no accepted native register or placement proof**. Three bounded diagnostic combinations also fail. IR checks and expected-failure reproduction are recorded separately from successful compilation. Restructuring branch-local value lifetimes remains implementation work.

One actual native size improvement is verified independently: unchanged reset C/C++ under `-Oz` produces a 66-byte leaf and 68-byte fragment, down from 78/80; the original is 62. Physical GP operands reduce from four to three. Clock query/fields remain 196/38. Synthetic jump witnesses check two-byte resolved C.J and four-byte external JAL x0 geometry, without supplying an original entry adapter or allocating space. No original image is changed and no BIN is generated.

Use `sh experiments/tsl9-v4160-interrupt-registers/verify.sh --language both`. Source, ABI counterevidence, independent tests, successful bounded probes and failed new native profiles are under `analysis/v4160-placement-2026-10-21/`, with English and Traditional Chinese guides separated. Destination/checkout verification produces fresh local results; historical build archives are not shipped. Linux/macOS, original intermediate IRQ state, ROM, board, Flash and rebuilt-image OTA remain unverified.

## Reset memory initialization

The reset slice at `0x186BA..0x186F8` now has a readable C/C++ implementation: separate GP observations, interleaved forward word copy, unsigned bounds, BSS word clear and the normal boundary A0/A1/A2 values. The exact ID2966 source proof covers 62 bytes / 17 instructions and rejects 17 raw mutations. Its 128-byte initializer is read as data. Each host language passes five groups / 338 cases / 133,601 checks; the independent review adds five groups / 538 cases / 193,964 checks per language and rejects 22 actually compiled mutants in total.

The original slice falls through into CSR setup. Its normal A0/A1 values survive the original clock initializer to the unresolved ROM entry, so a conventional C helper cannot silently discard them. A separate 372-byte / 130-instruction reset/clock caller proof documents that boundary. Installed ROM identity and interrupt compatibility remain unproved.

The native leaf compiles to 78 bytes / 24 instructions versus the original 62-byte slice. It has a C-generated return, while the optional continuation fragment produces 80 bytes and a four-byte JAL even though its source requests `c.j`. Neither fits the original extent. Numeric continuation linking at a nonoverlapping diagnostic address is only a relocation witness; it does not supply the original entry adapter. Full instruction-byte, register, memory-width and loop-CFG checks are separate from native all-path or asynchronous-state equivalence. No original image is replaced and no BIN is generated.

Use `sh experiments/tsl9-v4160-reset-memory/verify.sh --language both`. The source, caller, independent C/C++ and compiler review records are under `analysis/v4160-reset-memory-2026-10-21/`. Selected review source/text and receipt metadata are delivered; historical build archives remain in the workspace, while destination verification creates fresh local outputs. Windows results do not establish Linux/macOS or POSIX-shell launch success.

## Clock normal-return register contracts

The user reported successful official-BIN selection and firmware update through `tsl9-morphe` on 2026-10-21. This is an official-image OTA baseline reported by the user, with exact APK/BIN identities and versions still unspecified. It is separate from the rebuilt-image boot, acceptance and recovery requirements below.

The clock reconstruction now includes the original path-specific A3 value, conditional A2 assignment, query A4/A5 and the full field-function A5 product. A new 298-byte / 98-instruction caller witness and 130 inspected passthrough rows show A3 surviving to the unresolved callback at `0x131E0` through a fresh pointer at `0x4004C`. The concrete continuation after `1973C` is `9F4C`, then `131C2`. This makes discarding A3 unsafe without further evidence; it does not prove the callback consumes it.

The new C11/C++17 host suite passes six groups / 293,845 checks per language; independent tests pass four groups / 5,345 cases / 250,316 checks and reject sixteen actually compiled residue/A2 countercases in total. The unchanged 214-byte / 69-instruction source proof and fifty raw controls are reused, and original integer destination fields are checked separately.

Native builds use compiler register reservations and explicit physical-register constraints. The query uses only A2–A5, with A2 reserved from general allocation; its body is 196 bytes versus the original 174, leaving a 22-byte placement gap. The field body is 38 bytes versus the original 40. Its complete ten-instruction machine pattern confirms unsigned division, byte/halfword stores and normal-return A4=1000/A5=full product. These component proofs do not establish asynchronous intermediate-state, IRQ, full-image, ROM or physical compatibility. No original body is replaced and no BIN is produced.

Use `sh experiments/tsl9-v4160-clock-registers/verify.sh --language both`; native CLI and evidence limits are under `analysis/v4160-clock-abi-2026-10-21/compiler-review/`. Linux/macOS and POSIX-shell execution remain unverified while the previously observed CI account restriction is unresolved. New documentation remains split by language.

## Readable native clock and derived fields

The two clock functions now have a separate readable C/C++ implementation with actual volatile MMIO/RAM accesses and live GP primitives, without the older register-interpreter adapter. It reuses the unchanged 214-byte / 69-instruction source proof and 50 raw negative controls. Each host language passes six groups / 269,618 checks. Independent tests pass four groups / 5,345 cases / 214,811 assertions per language and reject ten actually compiled countercases in total.

Freestanding C11 and C++17 RV32 builds each produce a 170-byte query and a 44-byte derived-field function. The latter exceeds its original 40-byte extent, so these bytes cannot be substituted at the original placement. Linked components have no undefined symbols, runtime helpers or writable data. Full ELF-bound disassembly coverage verifies four/three GP read sites, load/store widths and direct branch boundaries; LLVM IR checks the dynamic GP offsets and unsigned arithmetic. Ten compiled native source controls and 24 disassembly-transcript controls are rejected in total. This is structural evidence, not a native all-path semantic or original register/stack/interrupt ABI proof.

Use `sh experiments/tsl9-v4160-native-clock/verify.sh --language both` for source/host checks. The standalone LLVM CLI is documented in `analysis/v4160-native-clock-2026-10-21/native-review/readme.en.md`. No RV32 code is executed or emulated, no original image is changed and no new BIN is generated. New guides and review documents have separate English and Traditional Chinese files; each `README.md` only links the language versions.

## Readable native interrupt initialization

The new component reconstructs `0x9A42` and four RCC helpers as readable C/C++, with direct volatile MMIO and CSR instructions in native builds. The original five functions occupy 264 bytes / 94 instructions; 94 raw instruction mutations are rejected. Each hosted language passes 4 groups / 6,680 checks; independent tests pass 4 groups / 34,267 assertions per language and reject six actually compiled countercases.

C11 and C++17 also compile and link as freestanding RV32 components: four 22-byte helpers and a 118-byte initializer. Both LLVM IR and actual machine-code checks identify the 20 ordered effects, including six fresh RCC reads, exact word/byte widths, CSR clear/set masks and the final RMW return value. Eight compiled native mutations are rejected. These are standalone component checks. There is no full-firmware replacement, original stack/register ABI proof, RV32 execution or physical I/O. The existing 691-section / 8,280-relocation image and its one unresolved resident entry remain unchanged.

Use `sh experiments/tsl9-v4160-interrupt-init/verify.sh --language both` for its separate source/host check. Native checks require LLVM and the explicit CLI documented under `analysis/v4160-interrupt-init-2026-10-21/native-plan/`. The previous cross-platform CI attempt was blocked before any steps by GitHub account billing/spending-limit restrictions; no rerun or billing changes were made.

## Portable entry and clock calculation

The portable Python backend verifies four models: runtime-loop, system-clock-query, resident-entry and resident-copy. Each checks its sealed source proof and then builds and runs our own C11 and C++17 host tests. Windows native compiler results pass; Linux, macOS and shell launch results require separate CI evidence. PowerShell and CMake are not dependencies of this entry.

The new clock-query model covers ID2966 V4.1.60 addresses `0x18834..0x188E2` and `0x1973C..0x19764`: 214 bytes and 69 instructions. Its source proof rejects 50 raw operand mutations. Each language passes 7 groups and 1,414 checks. It retains separate RCC reads, live register/address changes, a live prescaler table, unsigned arithmetic and width-limited stores. The initializer integration binds only the two proven call sites; the intervening call remains opaque.

## Earlier reconstructed models

| Model | Source evidence | Host tests per language |
| --- | --- | --- |
| Runtime main, initializer, loop and dispatcher | 220 bytes / 80 instructions; 45 raw mutations rejected | 6 groups / 1,431 checks |
| Reference resident entry, initializer and RAM seed | 230 bytes / 66 instructions plus 4-byte header; 35 raw mutations rejected | 5 groups / 121,496 checks |
| Reference byte copy | 58 bytes / 18 instructions; 23 raw mutations rejected | 5 groups / 772 checks |

These counts describe selected source and synthetic host behavior. Original firmware is data; it is never executed or emulated. The captured resident candidate lacks original bytes at `0x6EB2C`; a synthetic continuation cannot establish the missing implementation.

## Migration and evidence limits

The migration inventory records 116 historical PowerShell scripts and 93 root suites. The four portable models do not replace historical RV32/ELF, integration or download gates. The new downloader prototype supports dry-run and an offline HTTP boundary double only; its 23 cases are not a live vendor-download result.

Source proofs are under `analysis/*/source/`. Full local independent and composition receipts may bind host executables and logs excluded from publication. `publication-manifest.json` verifies the files actually shipped. Historical sealed documents retain their bytes; new user guides have separate English and Traditional Chinese files.

WCH CH32V20x is a hardware hypothesis, not a confirmed TSL9 part. Installed ROM, board, startup/interrupt ABI, physical Flash behavior and BLE OTA acceptance remain unproved. The existing 76,800-byte source-identical offline image remains **NOT-FLASH-VALIDATED**.
