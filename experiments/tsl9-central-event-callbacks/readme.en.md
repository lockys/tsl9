> Historical experiment snapshot. Current curated source/original-coordinate proof: [analysis/central-callback-integration-2026-10-26](../../analysis/central-callback-integration-2026-10-26/readme.en.md).

# Central-role event and helper bodies: C/C++ experiment

Reconstruct **1,938 bytes / 645 original instructions** across five helpers and one event callback. C and C++ produce identical RV32 objects. All 147 actual FUNC regions, 97 direct control relocations, and two address-reference pairs match the original BIN. Register-bound C retains explicit assembly ports and requires original coordinates and private calling conventions.

| Original range | Bytes / instructions | Confirmed static structure |
|---|---:|---|
| `0x10CE0..0x10D2E` | 78 / 26 | Length/type field search with pointer and length outputs |
| `0x110F8..0x11252` | 346 / 121 | Record loops, state accesses and ROM calls |
| `0x11252..0x11266` | 20 / 6 | Shared register-indirect ROM tail |
| `0x11266..0x11356` | 240 / 88 | Record comparisons/state updates; tail to `0x11252` |
| `0x114E2..0x11544` | 98 / 30 | State updates and callback forwarding |
| `0x11544..0x119C8` | 1,156 / 374 | Guard for event values 0..16; seven table targets |

A conservative static CFG reaches all 645 retained instructions. Two opaque ROM tail boundaries remain explicit. The already curated neighbor at `0x11356..0x11442` is excluded.

Partially linking these bodies, the previous three callbacks, and the accepted component yields **66,600 CODE bytes, 3,830 DATA bytes, and 4,967 relocations**. All eleven external CODE dependencies bind. Every prior allocation, 71 CODE aliases, and six DATA labels remain intact. The event table at `0x1A548` remains unprovided DATA, alongside the previous eight undefined symbols. Compiler undefined counts do not enumerate all runtime gaps.

**Not yet curated into `src/`; formal coverage stays at 89.03%.** No original-coordinate diagnostic link, BIN generation, target execution, or hardware access occurred in this experiment. Installed MCU/ROM/RAM/IRQ/BLE OTA contracts and global state bounds remain unproved. This does not establish full original-source recovery or flashability.

## Local replay

Run from the repository root. Set `LLVM_BIN` to the NDK LLVM directory matching the hashes in the spec.

```sh
python experiments/tsl9-central-event-callbacks/audit-v1.py
python experiments/tsl9-central-event-callbacks/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-central-event-callbacks/integrate-v1.py --tool-dir "$LLVM_BIN" --trial component-v1
```

First build the [three previous callbacks](../tsl9-central-callback-leaves/readme.en.md) and retain the accepted parent component. Trial folders are create-only. For an existing `native-v1`, replace `--trial native-v1` with the build script's `--replay experiments/tsl9-central-event-callbacks/build/native-v1`. These checks inspect instructions/objects and cross-compile without running firmware.

Next: provide and verify DATA/CODE relationships for the event jump table and two callback tables, then curate the sources and original-coordinate integration. Potential additions include RSSI connection diagnostics, event tracing, and field-parser diagnostics. They are not implemented and add no hardware-control behavior here.

[繁體中文](README.md) · [C source](src/central_event_callbacks.v1.c) · [Evidence summary](summary.json)
