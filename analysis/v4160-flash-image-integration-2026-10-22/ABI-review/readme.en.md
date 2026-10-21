# IRQ and Flash whole image: independent ABI/link review

Actual C11 and C++17 whole-image artifacts pass the bounded static checks. **20 actual-artifact byte controls per language** are rejected. The 76,800-byte image SHA-256 is `de159bb345b27250a683e197dd84b04e51a7a7ed89315347395baaea53f68be1`. This admits the stated storage, role and normal-return boundaries; hardware, ROM, OTA, nonreturn and asynchronous equivalence remain unproved. [繁體中文](readme.zh-TW.md)

## Findings

- All 691 allocations retain original addresses, sizes, kinds, flags and alignment. The actual merged and linked contents of 680 outside allocations are unchanged.
- Eleven readable C functions occupy 526 bytes: IRQ main144 plus four30-byte RCC helpers; six Flash functions64/8/30/14/46/100. Every linked body equals its immutable normal-contract component byte for byte.
- All 8,259 outside RELA retain their complete semantic digest. The new object has 8,270 RELA: those outside roles plus11 typed JALs. Actual instructions establish each destination, `rd=1` and an admitted RA continuation boundary.
- All53 section-relative bindings and original global/weak/nonmetadata local/SECTION roles remain. The six private Flash loop labels each had one same-owner branch use. Their actual linked branch targets discharge those labels without false numeric aliases.
- All20 known incoming calls retain actual instruction width, destination and RA contract. `9D00` and `9E7A` are two-byte C.JALs; `18906` is a `JAL x0` tail jump and creates no new RA.
- Metadata exceptions are exact: six `$d`→`$x` changes, six each unreferenced comment/ABS attributes/FILE additions, then42 unreferenced comment mappings removed at final link. No nonmetadata role is exempted.
- The690 file-backed allocations cover all76,800 bytes exactly once, with no holes, overlaps, padding or extra allocation. There are70 differences from the original and62 from the previous IRQ image, all inside the11 selected functions.
- Fifteen actual LOAD segments cover all691 allocations exactly once. Memory/file lengths, physical/virtual addresses and member permissions are checked separately, rejecting unowned memory tails or writable code.

`receipts/c.json` and `receipts/cpp.json` bind actual `formal-final` artifacts and producer receipts; `report.json` records selected hashes. Source provenance,42 compilation units, dependency and tool-command closure belong to the producer and source review evidence. Reading a producer receipt is not recompilation.

## Portable replay

From the project root, this command reads artifacts, parses ELF and decodes instructions without executing target code:

```sh
python3 -B apk-analysis/tsl9-v4160-flash-image-integration-2026-10-22/ABI-review/check_seal.py --project-root .
```

Independently review a freshly built C or C++ directory:

```sh
python3 -B apk-analysis/tsl9-v4160-flash-image-integration-2026-10-22/ABI-review/review.py --project-root . --folder PATH_TO_MODE_DIR --receipt review-result.json
python3 -B apk-analysis/tsl9-v4160-flash-image-integration-2026-10-22/ABI-review/review.py --project-root . --replay review-result.json
```

The directory needs `source-integrated.o`, `ADDRESS-WITNESS-ONLY.elf` and `NOT-FLASH-VALIDATED-irq-and-flash.bin`. An optional `verification.json` is additionally hash-bound with its language mode. `sh .../review.sh` accepts the same arguments; Windows can use `python -X utf8 -B`. The shell wrapper received static inspection only; no Linux, WSL or Git Bash execution occurred in this review.

The pinned `source-baseline.json` contains facts derived from actual prior objects, the original allocation manifest and sealed components: section/role digests,20 original incoming calls,11 component bodies and the previous IRQ image's eight-byte delta. **Archived W-path objects/ELFs are unnecessary.** The pinned original firmware and project source evidence/decoders remain required. `--firmware` and `--parser` allow explicit same-hash alternate locations. Standard portable replay does not regenerate the archived source baseline and records `archived_source_replay=false`.

## Boundary limits

Normal-return admission retains the instruction-level component conditions: completed accesses, terminating polls, valid frames and no unmodelled asynchronous interference. Component identity binds GPR residues, fresh frame reloads, the32-byte Flash wrapper and `SP+12` source slot,64 word transfers and CSR boundaries.

The original program instruction boundary at `+8` remains lost and a new `+10` boundary exists. Five preserved known loop roles do not prove all possible interior entries equivalent. Early CTLR scratch uses A2 instead of original A5; wrapper/IRQ save orders also differ. Full fault/nonreturn GPR prefixes and pointwise interrupt/asynchronous behavior remain unproved, as do unknown computed incoming references. `__tsl9v4160_rom_entry=0x40000` is a numeric link witness without a ROM implementation proof.

No target ISA execution/emulation, device operation, network request or flashing occurred. `NOT-FLASH-VALIDATED` remains applicable. This is not evidence of hardware success, recoverability, MCU identity, physical Flash capacity or OTA compatibility.
