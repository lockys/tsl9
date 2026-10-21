# Verified milestones

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
