# Independent OTA dispatcher HOST/native review

[繁體中文](README.md)

This bundle independently reviews the shared readable C/C++ for ID2966 V4.1.60 `0x9C4A..0x9E5C`: originally 530 bytes, 169 instructions and a 48-byte frame. The original BIN is read-only validation data. The new component is not integrated into the complete image.

## Actual results

Each C11/C++17 independent hosted run passes 16 narrative cases, 18 dispatches and 898 behavioral assertions, plus four actually compiled and assertion-rejected semantic controls. Fixture capacity guards and initialization do not inflate that assertion total. Cases cover command width, ordered W guards and word reads, conditional quarter counts/live values, saved/fresh S mode, live GP/payload/SP/context, distinct U/E/R guards, UNKNOWN UID and selected HALT/TRANSFER prefixes. The controls truncate the command, retain stale post-UID payload, force S active to one, and read RAM before Flash. The old exhaustive per-effect cutoff matrix is not rerun.

Both selected final native objects contain one real **776-byte / 285-instruction function with a 112-byte frame**, exceeding the original extent by **246 bytes**. The earlier 752-byte draft is not current evidence. Every raw field agrees with independent LLVM text operands. Four actual resource/compile/IR/disassembly recipes, three project dependencies plus the observed compiler `stdint.h`, source/tool hashes and receipt associations are independently read back. Three raw controls reject an entry SP add, removed JAL link and GP-read-to-write change.

Nine true UND obligations remain: six direct callee identities and three callback-address identities. The 23 RELA records are fifteen direct JALs and four HI20/LO12_I address pairs; one additional indirect copy call reads a fresh 32-bit slot4C pointer. These fifteen compiled calls are not address-ranked against thirteen original sites. No stub, numeric ABS provider, linked witness ELF or BIN is created. The sole ABS entry is exact nonprovider `STT_FILE ota_handler.c` metadata.

## Limits

Synthetic CALL providers may explicitly change named values, ambient arguments and memory; memory providers cannot silently mutate the frame. Unknown UID output never becomes an invented zero. Halt/transfer preserve earlier effects. This is a conditional hosted contract, not target execution or an ISA interpreter. Hosted live-SP fixtures do not prove physical native stack/alias behavior.

Native behavior assumes ordinary C callee preservation. Defined-argument masks describe a subset, not complete physical raw-register equivalence. The source-backed W A3/A4/A5 reply projection is retained without extending that claim to every call. The pinned original 51 owned relocations, 23 owner symbols and `14094→9C4A` incoming role are preserved as source evidence; their whole-image replacement obligations are not discharged. Placement, larger-frame safety, ROM/IRQ/BOOT/Flash/OTA compatibility and recovery remain unproved.

`selected.json` records source and actual result pins. The seal includes source/metadata only, never generated objects, executables, IR or build archives. Metadata success is not archive replay.

## Run

Paths below start at this case directory. `ROOT` is the actual project root. Both original `apk-analysis/tsl9-...` and published `analysis/...` evidence layouts are supported.

```sh
python3 -B ABI-review/check.py --project-root ROOT
python3 -B ABI-review/run-host.py --project-root ROOT --language both
python3 -B ABI-review/run-host.py --project-root ROOT --replay HOST_RECEIPT.json
python3 -B ABI-review/review.py --project-root ROOT --folder NATIVE_MODE --receipt NEW_REVIEW.json --firmware OFFICIAL.bin
python3 -B ABI-review/review.py --project-root ROOT --replay NEW_REVIEW.json --firmware OFFICIAL.bin
```

New hosted builds are create-only under this scope's `build/`. A pinned executable machine guard runs before/after every local test launch and rejects RISC-V. `--draft` is a positive-only unsealed-source diagnostic, not the selected formal result. Hosted replay reads archived files without compiling or launching them.

Native review consumes actual formal `verification.json`, object, IR, MD and disassembly. Its create-only receipt must be outside that producer directory. Omitting `--firmware` means no original BIN is opened; replay preserves that mode. Pure API: `native.py: inspect(root, folder)`; wrapper: `review.py: inspect(root, folder, firmware=None)`. Shell entrypoints accept the same arguments; `PYTHON` selects Python.

Default metadata flags `actual_host_artifacts_replayed` and `actual_native_artifacts_read` are false. Explicit replay/review emits the applicable true flag. Full ABI, placement and hardware OTA admission stay false.
