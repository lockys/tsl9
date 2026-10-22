# Fixed register banks and an original callback dependency

[繁體中文](README.md)

One source-derived complete register bank per entry was genuinely compiled as C11 and C++17. Separately, the original `0x1987A→0x188E2` dependency was closed within explicit premises. **Successful compilation does not prove original ABI compatibility. No new BIN or provider promotion occurred.**

| Selected entry | Original bytes | New bytes / instructions | Additional own writes | New frame |
| --- | ---: | ---: | --- | ---: |
| compare `0x200004BC` | 62 | 60 / 23 | RA, SP | 16 bytes |
| fill `0x2000039C` | 46 | 68 / 24 | RA, SP, A2 | 16 bytes |
| copy `0x20000332` | 58 | 64 / 22 | RA, SP | 16 bytes |

The sealed shared algorithms and real volatile IO remain unchanged. Only help-advertised `-ffixed-xN` flags were added. Previous extra scratch writes disappear, but all three entries add stack/RA effects before the original guard; fill also temporarily writes the originally preserved A2. Restoring registers on normal return does not establish prefix equivalence. This measured recipe cannot directly replace the original leaves.

Six actual ET_REL objects retain eleven genuine global FUNC definitions each. Complete compare/fill/copy objects allocate454/492/418 bytes and171/187/155 instructions, UND0/RELA0, including ten unselected functions each. The three selected entries total192 bytes/69 instructions across separate objects, not an integrated image. [Compiler implementation](implementation/readme.en.md); [independent raw-operand, IR and ABI review](abi-review/readme.en.md).

Original V4.1.60 ranges `0x188E2..0x1892E` (76 bytes/25 rows) and its sole dependency `0x19160..0x1917E` (30 bytes/12 rows) were read. Callback input `0x40012400` selects mask `0x200`: OR a fresh32-bit read of `0x4002100C`, then read again and AND ~mask. This does not restore the initial whole register value. Under valid private-stack, normal-access, nonaliasing and no adverse asynchronous modification premises, this closed chain preserves SP/RA/S/GP/TP. Five raw operand controls reject; optional existing ELF evidence covers only two byte slices, not whole provenance or installed identity. [Source contract and checker](adc-review/readme.en.md).

The next source gap is `0x19896→0x1892E`. Whole callback/config52 lifetime, ROM providers, actual hardware, Flash/NV ownership, interrupts and BLE OTA compatibility remain unproved. The existing550-byte component and77,824-byte NOT-FLASH-VALIDATED image remain unchanged.

Feature proposal: an offline compatibility report exposing original/rebuilt own-write banks, stack prefixes, extents and unresolved dependencies. It is not an implemented hardware feature or a substitute for physical validation.

Default parent/child checks validate metadata, not actual object reads; explicit receipts/firmware select actual-read modes. No HOST MMIO adapter, RV32/ISA emulation, hardware, linking or new BIN was executed. Python entry points were verified. Git Bash could not start (`NtCreateDirectoryObject 0xC0000022`); shell runtime remains unverified, with no bypass attempted.
