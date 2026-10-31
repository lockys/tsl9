# Six unresolved dependencies: static uses and boundaries

[繁體中文](README.md)

This ledger combines current original-address C/C++, existing original BIN instruction comparisons and conditional analyses. Addresses are V4.1.60 analysis coordinates. Uses are static observations or explicitly conditional inferences, not device execution. All six symbols remain unresolved; no alias, function, data or BIN is added.

| Dependency | Observed use | Still unproved |
| --- | --- | --- |
| `0x40000` | Reset transfers control from `0x18730` without writing a return address. A candidate SDK startup chain initializes RAM and uses `MRET`. | Whether the installed code and ABI match the candidate and startup completes. See [slot2 startup](../tsl9-resident-slot2-startup/readme.en.md). |
| `0x14056` | A linked call at `0x8A48` passes `a0=s3`, `a1=uint8(GP+0xA4)`, `a2=0x2000B9D8`, and `a3=uint16(GP+0x8E)`. The receive state machine writes data to that buffer at `0x8A1C`; normal length parsing permits 0–1040. See below. | The body remains excluded. The semantic model calls it a router, but actual dispatch, complete parameter ABI, return value and side effects are unproved. |
| `0x1AB48` | `0xA158` reads a halfword at `base+2*counter`; two direct writes use `(old+1)&3`. | Global counter range 0–3 at each read is unproved; if true, the existing 8-byte window covers that read. See [counter analysis](../tsl9-input-counter-data/readme.en.md). |
| `0x1A078` | `0xCF5A` reads `base+16*mode+column`, with column masked by 15. Conditional rows for modes 0–5 are in the source. | A setter accepts any low byte; locally observed 0–5 does not establish the global range or a complete provider. See [mode integration](../tsl9-record-mode-row-integration/readme.en.md). |
| `0x1A638` | `0x12046..0x1205E` prepares a six-byte comparison at `base+6*(2*channel+state)`; loop channel is 0–3. | State 0/1 at every read, the installed comparison slot and physical function remain unproved; if the stated conditions hold, the 48-byte window covers that comparison. See [sequence analysis](../tsl9-sequence-pattern-data/readme.en.md). |
| `0x1A69C` | At `0x131AA`, this address is passed in `a1` with length 4 in `a2`; `a0=*(GP+0x54)+12` to an indirect target loaded from `0x4004C`. The candidate slot has a byte-copy body; conditions appear below. | The four data bytes remain excluded and were not read or output. Installed slot identity and valid memory remain unproved. |

Register values, address formulas and conditional bounds do not establish reachability or the complete original C declarations. Addresses from different versions are not interchangeable. Installed ROM, RAM, IRQ and OTA compatibility are not demonstrated.

## Following the `0x14056` receive arguments

In the original V4.1.60 instructions, `AUIPC a2,0x20003` at `0x8A3A` and `ADDI a2,a2,-98` at `0x8A3E` compute `0x2000B9D8`. A separate PC-relative calculation at `0x8A12..0x8A1C` obtains the same base and writes a received byte at base plus counter. This supports identifying `a2` as the receive buffer; it is not a live RAM observation.

`0x89C2` and `0x89D6` construct the 16-bit length at GP+142. On the normal parsing route, `0x89E0..0x89E4` sends nonzero values above 1040 to a state-clearing path, with zero handled separately. After state and checksum comparisons at `0x8A2A..0x8A32`, `0x8A36` reloads that field into `a3`. Thus 0–1040 is conditional on normal length parsing, not a proved global invariant across all entries, alias writes, interrupts or callbacks. `a1` is the byte at GP+164; its specific command semantics are not established by that fact alone.

These observations agree with the existing [GATT receive model](../tsl9-v4160-gatt-ingress-model/README.md), which uses synthetic providers and does not establish `0x14056` internals or hardware behavior. The excluded function body was not read.

## `0x1A69C` and settings defaults

Original `0x131A6..0x131B4` loads the indirect target freshly from `0x4004C`, passing destination `*(GP+0x54)+12`, source `0x1A69C`, and length 4. The existing [SDK copy audit](../tsl9-resident-copy-arch/readme.en.md) identifies candidate slot value `0x20000332`; its 58-byte body copies bytes forward using source, destination and length, preceded by access to `0x4002420C` and `FENCE.I`.

According to the [settings initialization analysis](../tsl9-original-prebinding-settings/readme.en.md), if reset GP and the initial pointer are not overwritten, the destination is `0x2000C2A8..0x2000C2AC`. Its initialization path checks four bytes for ASCII 32–126 and may enter the default path when a byte fails. **If** the installed slot matches the candidate, source and destination are valid, and the call returns normally, the four source bytes are copied to that destination range. This does not establish the default content, actual setting semantics, execution on every boot, or physical ROM/Flash results; excluded data was not read.

## Local use of the `0x1AB48` lookup result

At `0xA146..0xA158`, the code uses `uint8(GP+176)` as an index and reads unsigned 16-bit value `x` from `0x1AB48+2*index`. On this path, `0xA15C..0xA166` computes `y=(x+0x802)&0xFFFF`; `0xA16C` writes its low 8 bits at `SP+10`, while `0xA168..0xA18E` writes bits 8–11 into the low nibble at `SP+9`, preserving its high nibble. Together these fields encode `(x+0x802)&0xFFF`. Relative to the later buffer start `a0=SP+4`, these are offset 6 and the low nibble of offset 5.

At `0xA1A8` the code calls `0xED00` with `a0=SP+4` and `a1=7`. The complete function initializes its sum from the first two buffer bytes, adds data starting at offset 3 for the byte length at offset 2, skips data index 7 and retains the low 8 bits. At `0xA1AC` the returned byte is stored to `SP+14`, which is buffer offset 10 / data index 7, then `0xA1B2` calls `0x12A08`. With a valid buffer, no interference and normal completion, this supports interpreting the result as an additive checksum; it does not establish protocol, units, actual transmission or product feature. See the [existing checksum comparison](../tsl9-feature-callback/readme.en.md).

This is static data flow for the lookup path, conditional on valid pointers and stack, no alias/asynchronous overwrite and normal callee execution. The index and resulting field have conservative byte and 12-bit widths respectively; neither proves the global index is 0–3 or that four entries constitute the complete table.

## Conditional dispatch after the checksum

`0xA1B2` passes that buffer to `0x12A08`. In the [original dispatcher](../tsl9-record-dispatch/readme.en.md), the function calls `0x81AA` first and returns if that result is zero and the first input halfword is not 1; otherwise it calls `0x821E` with 0 and returns if that result is zero. A nonzero byte at input offset 11 routes to `0x16B7C`. If zero, it assembles a stack record, uses the indirect `0x4004C` slot with input+3 as source and the byte at input offset 2 as length, then calls `0x18CA4` with `a0=0x40006400` and `a1=SP+12`.

The value `0x40006400` matches WCH CAN1 base. Mailbox selection and field operations in `0x18CA4` correspond to [WCH CAN_Transmit](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/src/ch32v20x_can.c). This supports an inference of submitting a message to built-in CAN1 **if the guards pass, input offset 11 is zero, and copy/callee contracts hold**. It does not establish physical hardware, wiring, valid data length, an available mailbox, successful delivery, or the alternative branch's purpose. The caller does not check the return from `0x12A08`. Indirect slot identity, callee effects and runtime modifications remain limitations.

## Data length and stack boundary

At `0xA0D4..0xA0E0`, source `s3`, destination `SP+4`, and length 12 are passed to the indirect `0x4004C` slot; if the slot is the candidate copy and the call returns normally, the initial 12-byte record used later comes from that input. At `0x12A32`, the dispatcher reloads record offset 2 as a byte length; `0x12A46..0x12A4E` passes `record+3`, that length, and the dispatcher's own `SP+23` to another fresh `0x4004C` call. No local upper-bound check was observed between those two instructions on this branch.

WCH's [CanTxMsg](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32v20x_can.h) defines an 8-byte Data field; `0x18CA4` reads all eight data bytes on a selected-mailbox path. If both indirect calls are the candidate forward copy, memory accesses are valid, and no other writes intervene, lengths below 8 copy fewer than eight data bytes and lengths above 8 extend beyond that field. In the 48-byte frame, saved S0 and RA are at `SP+40` and `SP+44`; counting from `SP+23`, lengths of at least 18 and 22 respectively touch those positions. This is **conditional address analysis**, not proof of an actual overrun, uninitialized content, reachable input, or vulnerability. Installed slot identity, prior validation, aliasing and asynchronous behavior remain unresolved; it does not justify modifying or flashing firmware.
