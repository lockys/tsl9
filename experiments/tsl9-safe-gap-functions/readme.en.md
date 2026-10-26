# Remaining CODE candidates

> Historical candidate snapshot. Curated source and original-address integration are now documented [here](../../analysis/safe-gap-integration-2026-10-26/readme.en.md). The old audit fixes the original158-file context;use the current integration/flow replay for the159-file source tree. Historical receipts remain unchanged.

[繁體中文](README.md)

Ten candidate bodies were reconstructed from eight windows in the official ID2966 / V4.1.60 image: **764 bytes and 288 original instructions**. The [C/C++ source](safe_gap_functions.c) preserves register data flow and explicit assembly ports. It requires the original execution context and does not expose a normal callable C ABI.

| Original entry | Static observation |
|---|---|
| `0x81CA` | Calls `0x81B0` and multiplies its return value by 1000; units remain unknown. |
| `0x9B02` | Registers `0x9AD2`, stores `GP+168`, then selects a tail call or a write to `0x40010814`. |
| `0x12A6E` | Uses the saved input to select a stack record passed to `0x18BA2`, or a call to `0x16C72`. |
| `0x13660 / 0x136D0 / 0x13740` | Request a length-12 buffer through a ROM pointer, fill tags `AB / BA / B9` and fields, then pass the shared callback `0x13F36` to `0x9124`. ROM allocation/free semantics and timing units remain unconfirmed. |
| `0x13DD4` | Registers itself, calls `0x13D48`, and conditionally schedules `0x13F88`. |
| `0x13F36` | Passes non-null record fields at `+0/+2/+4/+8` to `0x13E98`, then tail-calls a ROM pointer. Null returns immediately. |
| `0x14CC8` | Packs three `0x821E` results, a `0x829E` result, and raw bytes starting at `GP+352`; no invented Boolean normalization. |
| `0x16C72` | Initialization call sequence guarded by `((A0-1)&255)<=1`; the original full-width `A0` is still passed to callees. |

## Verified evidence

The [native/static receipt](audit-result-v1.json) records identical actual C11 and C++17 objects: 64 positive FUNC regions, 43 direct-control relocations and six CODE-address HI/LO pairs, totaling 55 relocations. Re-encoding their original addresses reproduces all 764 firmware bytes. Two independent ELF readers agree. All 17 standalone-object UND symbols match positive FUNC providers in the preceding diagnostic ELF.

Static traversal from each candidate entry covers all 288 instructions without an ordinary sequential or call-return-position gap, assuming calls return normally. **Three opaque indirect calls and four indirect tails** remain explicit; no substitute providers were introduced.

## Limits

A bounded scan of the preceding 23,314 selected instructions and aligned DATA words found no incoming references to these windows. It excludes the private body, other indirect sources and physical execution. The new candidates themselves contain three shared-callback references, self-registration and the `0x12A6E -> 0x16C72` call.

These candidates have not passed full source integration or actual original-address linking. **Formal curated byte coverage remains 94.54%**; these 764 bytes are excluded from that numerator. ROM identity/ABI, hardware startup, RAM, IRQ, OTA compatibility and working features remain unproved. No new BIN, target execution, emulation, hardware access or vendor-service request occurred.

## Reproduce

Run from the repository root. Set `LLVM_BIN` to the pinned LLVM tool directory. This receipt used Windows Android NDK 27.1 / Clang 18 and requires the preceding `secondary-message-v2` diagnostic ELF plus the exact spec-pinned tools and inputs. To replay retained outputs read-only:

```sh
python3 experiments/tsl9-safe-gap-functions/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-safe-gap-functions/build/native-v1
python3 experiments/tsl9-safe-gap-functions/audit-v1.py --tool-dir "$LLVM_BIN"
```

If `native-v1` does not exist, replace the first command's `--replay ...` with `--trial native-v1`. On Windows, `py -3` can replace `python3`. Outputs are ET_REL inspection objects, not flashable firmware.
