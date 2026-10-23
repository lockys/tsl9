# Channel routing and filter configuration

[繁體中文](README.md)

This milestone composes genuine C/C++ objects for the12ABE channel router, built-in CAN filter backend and external SPI filter backend. Reconstruction and checks remain offline. No reconstructed firmware has been validated on the original hardware.

| Scope | Actual result |
| --- | --- |
| Five new src units | 840B; original and curated C11/C++17 object projections agree |
| Four existing shared units | 402B of SPI transfer/write/modify and register read/write |
| Original-PC component | Six spans,1242B,445 instructions,94 strong FUNC; every code byte equals the official BIN |
| Extended receive/dispatch graph | 3166B,1104 instructions,191 FUNC,144 pending RELA; one direct UND:14D2E |
| Current source curation | 71 C/header files,45 native units,90 comparisons/180 objects; all prior80 facts unchanged |

The nominal ELF is a diagnostic component. Its RX LOAD spans68340B and includes67098B of unproved gaps. The VMA0 ET_REL graph retains pending controls and PC-sensitive arithmetic. Neither file is executable firmware or a flashable BIN. FUNC symbols represent architectural regions, not ordinary C ABI functions.

## Findings and boundaries

The router preserves full32-bit A0, tail-dispatches zero to128FE, and nonzero to16CC4 with A3=0.128FE uses a176B frame and fourteen filter descriptors after two opaque resident calls.18BA2 strongly matches the retained official WCH CAN_FilterInit structure and register layout. This identifies code structure, not the physical MCU.

16CC4 accepts a low-byte channel test, caps copied input at12B and configures six11-bit filter IDs. SPI02/03/05 and register layout support an MCP2515/MCP25625-compatible family candidate; the exact controller is unproved. Post-call SP/S-register values are fresh unknowns. A0 residue is not a generic success result.

The complete14D2E candidate spans1912B/666 instructions, including two relative jump tables and at least71 external direct targets. One remaining UND describes only this component frontier. See the [dispatch evidence](../../analysis/feature-dispatch-frontier-2026-10-23/readme.en.md).

## Reproduction

From the repository root, set LLVM_BIN to the existing tool directory whose hashes match spec.json:

```sh
python3 scripts/verify-curated-source.py --replay build/curated-source/channel-filter-20261023-v1/verification.json
python3 experiments/tsl9-channel-route/build.py --tool-dir "$LLVM_BIN" --output experiments/tsl9-channel-route/build/your-new-trial
python3 experiments/tsl9-channel-route/verify-v2.py --tool-dir "$LLVM_BIN" --folder experiments/tsl9-channel-route/build/your-new-trial/c --mode c --write
python3 experiments/tsl9-channel-route/verify-v2.py --tool-dir "$LLVM_BIN" --folder experiments/tsl9-channel-route/build/your-new-trial/cpp --mode cpp --write
```

Outputs are create-only. Source/dependency/tool/IR identities, ELF ownership, complete original bytes, parent preservation and corrupt-artifact rejection are checked. No HOST model, target, ISA emulator, hardware, network API or OTA executes. The recorded Windows toolchain was tested; other platforms require equivalent checks.

Frozen v1 code and receipts remain intact. Independent review identified two omitted resident-transfer sites in its full-graph count; v2 corrects this statistic and preserves the historical record. Original receipts stay local; anonymous public derivatives retain original SHA-256 provenance.

A useful proposed feature is an offline filter-configuration preview comparing fourteen built-in banks against six external IDs, including truncation and channel/backend differences. It is not implemented and requires no CAN transmission or hardware changes.
