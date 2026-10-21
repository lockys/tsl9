# Verified milestones

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
