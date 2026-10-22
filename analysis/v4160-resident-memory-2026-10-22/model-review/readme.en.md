# Independent resident memory-leaf review

[繁體中文](readme.zh-TW.md)

This review reads the compare, fill and forward-copy candidate bodies, readable C, authored HOST tests and actual C11/C++17 RV32 ET_REL files. It does not link, run RV32 code, export firmware or validate hardware.

## Source and behavior

`source-ledger.json` records complete bounded bodies, separate RAM/Flash mappings and hashes. Explicit `--candidate-refs` reads all six slices from the two existing reference segments. Agreement does not establish the installed resident version.

| Candidate RAM entry | Original bytes/instructions | Normal effect |
| --- | --- | --- |
| `200004BC` compare | 62/19 | Initial null/count0 returns0; each LBU is compared with full32 A1; all equal returns1 |
| `2000039C` fill | 46/14 | Ordered low8 stores; returns the advanced destination, or the initial destination on early exit |
| `20000332` copy | 58/18 | Fresh read before each forward store, including overlap feedback; returns initial destination |

All three read32/save `4002420C`, write32 zero and execute `FENCE.I` before initial argument tests. Normal exits restore the saved word. Addresses wrap as uint32; no additional null test is introduced inside the loop. The three original leaves total166B/51 instructions and have no own stack or nested calls.

## Independent results

The authored sparse-memory fixture is not a machine-code interpreter. Actual C11 and C++17 each passed **16 narratives and940 assertions**. They cover full32 expected values, mismatch stopping, fresh reads after synthetic edits, MMIO aliasing, fill end-pointer return, forward-copy feedback and wrapping through address0. HALT/TRANSFER/UNKNOWN retain only observed prefixes; the HOST budget is diagnostic. No physical fault/interrupt behavior is inferred.

Each language also compiled three single semantic mutations and rejected them through actual assertions: truncated compare argument, null bypass of the guard, and repeated first copy-source address.

| Actual C/C++ native function | Bytes/instructions | Measured frame |
| --- | --- | --- |
| compare | 146/61 | 48B |
| fill | 138/58 | 32B |
| copy | 160/64 | 48B |
| Source-declared static `begin` | 86/35 | 16B |

Total530B/218 instructions with13 CALL_PLT relocations. `begin` is an explicit source helper, not a machine outliner product; machine outlining is disabled. The independent reader compares every decoded operand with actual LLVM text and checks local CFG boundaries, saves/restores, AUIPC/JALR relocation roles, IR, exact sources/tools and `-MD` resource/header provenance. Public entries use hidden struct-result sret plus an explicit I/O context, not the original A0/A1/A2 leaf ABI.

Five genuine unresolved `ml_port_*` symbols remain. They are neither numeric ABS providers nor linked hardware implementations. Actual MMIO and `FENCE.I` still require providers. Original ABI, placement, installed identity, asynchronous behavior and OTA compatibility remain unproved. The530B total refers only to these four functions.

## Interfaces

Metadata/source-only default, with no generated build archive required:

```sh
python3 -B <case>/model-review/check.py --project-root <ROOT>
sh <case>/model-review/verify.sh --project-root <ROOT>
```

Explicit actual candidate/native reads, without target execution:

```sh
python3 -B <case>/model-review/review.py --project-root <ROOT> --candidate-refs <resident-reference-root>
python3 -B <case>/model-review/review.py --project-root <ROOT> --folder <native-mode-folder> --receipt <NEW-review.json>
python3 -B <case>/model-review/review.py --project-root <ROOT> --replay <review.json>
```

Authored HOST compilation/execution and separate read-only artifact replay:

```sh
python3 -B <case>/model-review/run-host.py --project-root <ROOT> --language both
python3 -B <case>/model-review/run-host.py --project-root <ROOT> --replay <HOST-verification.json>
```

The immutable HOST executable guard rejects target-machine execution. Native folders require the frozen producer receipt, object, IR, dependency file and four actual command logs. Only explicit artifact modes report `actual_native_artifacts_read` or `actual_host_artifacts_replayed` true. `selected.json` retains historical observations; it cannot replace fresh artifact review.
