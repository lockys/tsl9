# Published-script portability audit

This independent work inventories the published tree at commit `99de4f9d4da22f0cd28e039e0197defebf48fb72`. It changes no published file, destination checkout, sealed source proof or native verifier. It does **not** claim that all 116 PowerShell scripts have been ported.

| Static category | PS1 files |
| --- | ---: |
| Host C/C++ tests | 54 |
| Native RISC-V / ELF verification | 50 |
| Host tests plus RV32 compilation | 2 |
| Orchestration or evidence | 9 |
| Download | 1 |
| Total | 116 |

`inventory.json` records all 116 paths, SHA-256 values, parameter declarations, compiler flag literals, source/test paths, executable argument lines and proof-gate markers. It also records 33 published Python files and 28 BIN files. `suite-map.json` maps all 93 original root `-Suite` choices to existing entries. These are static literal mappings, not a PowerShell AST or proof that each entry is portable; dynamically assembled paths require review. Files in `tests/` that set their root to the parent are resolved accordingly.

## Migration facts

- MSVC `DevShell.dll` / `Enter-VsDevShell`, Windows NDK paths, executable suffixes and one absolute user Python path are explicit barriers. A shell that merely invokes PowerShell does not remove them.
- Host compile/run, raw-source proof, and RV32 ELF verification are different gates. The existing clock and memcmp entries run both host tests and a freestanding target compile. Porting only the host half must report the target gate as pending.
- Preserve C11/C++17 modes, warnings-as-errors, original source/fixture hashes, range checks, test arguments, seals and post-build input checks. For ELF work also preserve actual storage/symbol roles, exact relocation multisets, own-HI/LOW pairing and negative cases.
- The original root suites use different test arguments: repository root, Runtime plus BOOT, or no arguments. `host_runtime_argument_lines` retains their actual source lines; source/test literal and inferred-stem mappings must be reviewed before enabling a generic runner.
- Original inputs are already published. ID2966 V4.1.60 is 76,800 bytes with SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`. Legacy Runtime ID2581 is also 76,800 bytes but SHA-256 `32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc`. Selected BOOT ID2580 is 12,288 bytes, SHA-256 `650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb`. Do not substitute one Runtime for another.
- Five published source checkers were replayed successfully with explicit portable inputs: BOOT command, BOOT UID, resident-copy reference, resident-entry reference and V4.1.60 runtime-loop. They accept `--check`, `--firmware` or `--carrier`, and `--source-root`. The separately published `tx-source/check-source.py` has `--check` but lacks those root arguments; it is not counted as parameterized by this audit.
- Other Python files are reuse candidates only. A missing literal Windows-path match does not prove that an entire verifier is portable or independent of historical evidence.

## One bounded helper

`download_firmware.py` is a standard-library **dry-run / synthetic loopback-only** implementation of the existing downloader's catalog, response and first-stage decoding contract. `download-firmware.sh` calls Python directly, never PowerShell. This helper deliberately has no live vendor mode and accepts no real UID. It does not replace the original authorized live-download workflow.

| Original argument | New argument |
| --- | --- |
| `-FirmwareId` | `--firmware-id` |
| `-OptionsReceipt` | `--options-receipt` |
| `-OutputRoot` | `--output-root` |
| `-MockUri` | `--mock-uri` (HTTP literal loopback only) |
| No equivalent | `--dry-run` (zero requests and no output files) |

The decoder requires one terminal marker, CRLF-separated 2,048-hex-character pages, 1..96 pages and a response of at most 262,144 bytes. It decodes hex then XORs each byte with `0xB7`. Only validated content is saved, in a unique create-only directory with readback hashes. Errors do not log arbitrary responses or request identity. Requests use one attempt, no redirect, proxy or retry. Decoded bytes remain first-stage candidates: hardware applicability, execution and OTA readiness are false.

```sh
python3 -B download_firmware.py --firmware-id 2966 \
  --options-receipt tests/synthetic-catalog.json --dry-run
sh download-firmware.sh --firmware-id 2966 \
  --options-receipt tests/synthetic-catalog.json --dry-run
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
```

The Python helper's five test groups / 23 behavior cases passed on this Windows host. Dry-run uses the actual child-process CLI; response tests use the real decoder/persistence and an offline HTTP-boundary double. A stub first failed the dry-run requirement, and a port-zero regression was observed failing before correction.

Actual socket loopback was attempted and refused by the execution sandbox (`PermissionError`, errno 13, WinError 10013). Git for Windows `sh` was present but failed before reaching the wrapper (`NtCreateDirectoryObject`, status `0xC0000022`). Neither restriction was bypassed. **Socket integration, the shell wrapper's runtime behavior, Linux and macOS execution remain unverified.** These limits are recorded in `verification.json`; offline mock success is not a network or cross-platform runtime claim.

## Replay and scope

Inventory reproduction uses the fixed commit's path set, while checking the actual published worktree bytes. A later commit can add scripts without silently changing this 116-file baseline.

```sh
python3 -B inventory.py --published /absolute/published-checkout --check
python3 -B verify_migration.py --published /absolute/published-checkout --check
```

The second command is strictly readonly: it rechecks inventory and sealed members. A fresh test receipt can be created only in an unsealed copy with `verify_migration.py --run`; optional `--shell /path/to/sh` requires that actual wrapper execution pass. No compiler was installed or invoked by this audit, and no original/rebuilt firmware, ISA, BLE or hardware was executed. The parent's portable host runner is a separate workstream.
