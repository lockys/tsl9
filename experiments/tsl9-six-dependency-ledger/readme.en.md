# Six unresolved dependencies: static uses and boundaries

[繁體中文](README.md)

This ledger combines current original-address C/C++, existing original BIN instruction comparisons and conditional analyses. Addresses are V4.1.60 analysis coordinates. Uses are static observations or explicitly conditional inferences, not device execution. All six symbols remain unresolved; no alias, function, data or BIN is added.

| Dependency | Observed use | Still unproved |
| --- | --- | --- |
| `0x40000` | Reset transfers control from `0x18730` without writing a return address. A candidate SDK startup chain initializes RAM and uses `MRET`. | Whether the installed code and ABI match the candidate and startup completes. See [slot2 startup](../tsl9-resident-slot2-startup/readme.en.md). |
| `0x14056` | A linked call at `0x8A48` passes `a0=s3`, `a1=uint8(GP+0xA4)`, `a3=uint16(GP+0x8E)` and a PC-relative value in `a2`. See [incoming_protocol.c](../../src/native/receive/incoming_protocol.c). | The body is in the existing excluded range. Parameter meanings, the `a2` object, return value and side effects are unknown. |
| `0x1AB48` | `0xA158` reads a halfword at `base+2*counter`; two direct writes use `(old+1)&3`. | Global counter range 0–3 at each read is unproved; if true, the existing 8-byte window covers that read. See [counter analysis](../tsl9-input-counter-data/readme.en.md). |
| `0x1A078` | `0xCF5A` reads `base+16*mode+column`, with column masked by 15. Conditional rows for modes 0–5 are in the source. | A setter accepts any low byte; locally observed 0–5 does not establish the global range or a complete provider. See [mode integration](../tsl9-record-mode-row-integration/readme.en.md). |
| `0x1A638` | `0x12046..0x1205E` prepares a six-byte comparison at `base+6*(2*channel+state)`; loop channel is 0–3. | State 0/1 at every read, the installed comparison slot and physical function remain unproved; if the stated conditions hold, the 48-byte window covers that comparison. See [sequence analysis](../tsl9-sequence-pattern-data/readme.en.md). |
| `0x1A69C` | At `0x131AA`, this address is passed in `a1` with length 4 in `a2`; `a0=*(GP+0x54)+12` to an indirect target loaded from `0x4004C`. See [settings_defaults.c](../../src/native/startup/settings_defaults.c). | The four data bytes remain excluded and were not read or output. The target identity, valid memory, and whether it copies data remain unproved. |

Register values, address formulas and conditional bounds do not establish reachability or the complete original C declarations. Addresses from different versions are not interchangeable. Installed ROM, RAM, IRQ and OTA compatibility are not demonstrated.
