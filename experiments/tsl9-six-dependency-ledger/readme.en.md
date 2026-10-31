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

### The earlier checksum check alone does not bound length

`0xA062` calls `0x1069E`, which at `0x106A8` calls `0xED00` with excluded index 7 and then only compares the result with input offset 10, returning 1 on equality. `0xA066` exits on zero. The function itself does not compare the length; `0xED00` treats the byte at offset 2 as a 0–255 loop length and does not add that length byte itself.

For every byte length 0–255, in a **sufficiently long readable synthetic buffer**, set offset 2 to that length and all other bytes to zero: the sum and offset 10 are both zero, satisfying the checksum relation mathematically. This disproves the idea that checksum equality alone implies length at most 8; it is not execution of the original program and does not prove those records pass other guards or reach the later copy. Memory consistency between the calls remains unknown.

### One upstream record dispatch entry

The in-scope dispatcher reads a halfword from record `s0+0`. In the corresponding dispatch tree, `0x14F18..0x14F1C` compares it with **880 / `0x370`** and branches on equality to `0x152D0`; that block moves `s0` to `a0`, restores its own frame, and tail-jumps to `0xA054` at `0x152D8`. Thus `0x370` is the compared record value for **this path**, not proof of all entries or the data source. The tree also depends on the earlier `0x829E` result and other branches; no comparison there directly establishes the offset-2 length.

Together with the subsequent WCH CAN1 interface comparison, `0x370` is a message identifier lead to validate. Without an actual CAN capture, complete original-device ingress or feature evidence, it is not an established CAN ID, device behavior or length guarantee. See the [feature dispatcher](../tsl9-feature-dispatch/readme.en.md).

### The queue length-4 check belongs to another branch

The original queue consumer `0x12C86..0x12CA4` selects a record with a 12-byte stride and requests a 12-byte copy to its own `SP+8` through the indirect `0x4004C` slot. It then calls `0x82D2` at `0x12CB0` and continues only on zero; `0x12CB6..0x12CBA` freshly reads the stack record's first halfword and compares it with `s4`. Queue entry sets `s4=1`; **if that value is preserved across calls**, a non-1 first value branches to `0x12D78`, bypassing the offset-2 equals 4 check at `0x12CBE..0x12CC4`. That branch has its own settings-bit and `0x81AA` guards and passes `SP+8` to `0x14D2E` at `0x12D8C`.

Thus, if the upstream record's first value remains `0x370` at the relevant reads, it takes the non-1 branch and the other branch's length-4 check cannot be used to bound it. This is **conditional branch analysis**: indirect copy, `0x82D2`, preservation of `s4`, stack and memory across calls, the record's actual producer and other validation remain unresolved. It does not establish a reachable length or vulnerability. See the [queue source](../../src/native/receive/queue_consumer.c) and [feature dispatcher](../tsl9-feature-dispatch/readme.en.md).

### Two identified queue insertion paths

`0x12BC8` selects among up to 32 slots of 12 bytes, stores the low halfword of `a0` at offset 0 and low byte of `a2` at offset 2, then requests a copy to offset 3 through `0x4004C` using full `a2`; its body has no length upper-bound check. PC-relative calculations for the [original-layout reconstruction](../tsl9-ring-insert/readme.en.md) and the queue consumer both point to `0x2000C038`. The shared numerical address alone does not prove physical memory ownership or unchanged data across calls.

| Identified source | Original handling before the `0x12BC8` call | Static boundary |
| --- | --- | --- |
| SPI receive `0x16ACC..0x16AFA` | Masks the byte at `SP+20` to four bits and accepts only `(length-1)&255 <= 7`, passing that length in `a2`. | **1–8** at this callsite, conditional on normal execution and undisturbed registers/stack. |
| Candidate CAN1 IRQ `0x12C24..0x12C4A` | `0x18D9C..0x18DA2` stores the source word's low four bits at output structure offset 10; the IRQ reads its own `SP+22` as `a2`. | **0–15** if the provider completes normally and stack/registers are unchanged; instructions alone do not establish which DLC values physical hardware actually supplies. |

These are identified callsites, not an exhaustive list of all possible producers; they do not prove which source produced a particular `0x370` record. Candidate copy, later slot/consumer behavior, IRQ and memory consistency must hold before extending a source bound to later uses. No firmware or hardware was executed.

### Candidate CAN1 receive layout versus WCH

Original receive function `0x18D78` writes identifier type, ID, RTR, low-four-bit length, eight data bytes and FIFO metadata into a caller-provided structure. The fields and FIFO-release flow correspond to [WCH CAN_Receive](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/src/ch32v20x_can.c) and the [CanRxMsg definition](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32v20x_can.h), supporting a CAN receive helper inference without claiming complete equivalence.

IRQ `0x12C32` passes `SP+12` as the structure base in a 32-byte frame, making DLC `SP+22`, eight Data bytes `SP+23..SP+30`, and FMI `SP+31`. `0x12C3C..0x12C4A` passes `SP+23` and DLC as the ring source and length. The ring slot's 8-byte data window is offsets 3–10; offset 11 is assigned tag 0 after the copy.

**If** DLC is 9, both helpers complete normally, `0x4004C` is the candidate forward copy, and memory/registers are undisturbed, the copy reads FMI at `SP+31` into slot offset 11, which the subsequent tag 0 overwrites. If DLC is at least 10, numerical ranges extend outside the IRQ frame and beyond that slot. This is conditional source/destination range reasoning, not proof DLC 9–15 occurs on the device, that the path is reachable, an actual overrun, or a vulnerability; it cannot establish vehicle behavior or flashing safety. No hardware was accessed.

## Local normalization of `0x1A638` sequence state

`0x12046` first reads the current channel state to prepare the comparison at `0x1A638+6*(2*channel+state)`. After the indirect comparison returns, the equal branch **reads the state byte again** at `0x12066`, computes `t=(v+1)&255` and stores it at `0x12072`. If `t<=1`, it retains `t` and exits. If `t>1`, the path through `0x1207A..0x12090` then clears that state to 0. The unequal branch clears it directly at `0x1209C` before considering the next channel.

Exhaustively enumerating `v=0..255`, the equal branch leaves only 0 or 1 after normal completion: `v=0` yields 1, `v=255` wraps to 0, and all others become 0 after the second store. The unequal branch stores 0. This is a **single completed local transition**, conditional on valid memory, correct `s5`/`s6`/channel relationship, normal indirect call and path completion, and no alias/IRQ/DMA/reentrant overwrite. When `t>1`, that value exists transiently between `0x12072` and `0x12090`. The first lookup precedes normalization, and the two state reads can differ. This does not establish that each lookup index is 0/1, absence of intermediate states or a global state bound. See the [existing sequence analysis](../tsl9-sequence-pattern-data/readme.en.md).

### Completion marker data flow

When the new matched state exceeds 1 at `0x12076`, `0x1207A..0x1209A` reads three bytes from `s2+0..2` and combines them with `0x80+channel` as `word=(byte0<<24)|(byte1<<16)|(byte2<<8)|(0x80+channel)`. Normal loop channel is 0–3, so the low byte is `0x80..0x83`. The corresponding state is cleared before the jump to `0x11C64`.

On the branch where byte `0x2000BFD3` is zero, `0x11C7A..0x11C96` stores 1 there, stores the word at `0x2000BFCC`, clears `0x2000BFD0..0x2000BFD2`, then twice freshly loads and calls an indirect target from `0x40058`, with `a1/a2` respectively `1/480` and `2/640`; each `a0` is read from byte `0x2000BFC8`. This is **conditional static data flow**: valid pointers, stack, memory and indirect-callee preservation/return contracts are required. The numbers 480/640 do not establish time units or successful scheduling. A nonzero status byte takes another branch; these observations neither identify a hardware button/product feature nor prove a physical match occurred.

### WCH V1.30 function-table candidate

A locally retained [fixed-version WCH V1.30 header](https://github.com/openwch/ch32v20x/blob/ec059e0b18046b111ee850e44f105fcd095e775c/EVT/EXAM/BLE/LIB/wchble_rom.h) uses default table base `0x40034` and reads `base+4*n` for `BLE_LIB_JT(n)`; its `tmos_start_task(taskID,event,time)` uses slot 9, so that candidate table entry is `0x40058`. The same header describes a 625-microsecond event timer unit. Header SHA-256: `647a185941fedeb6ba16d544d9bca91a6f53219bb649a5513b59abeb21a9a94c`.

**If** the installed slot is compatible with that V1.30 interface and timer unit, task ID/event values are valid, and the calls return successfully, the two calls can be interpreted as events `1`/`2` after 480/640 ticks, nominally **300/400 milliseconds**. This is a conditional comparison against a public candidate interface, not a measurement of time, proof of slot contents/function ABI or successful execution, or identification of a button or product feature. The V1.30 header does not identify the installed resident version.

On the other branch where `0x2000BFD3` is nonzero, `0x12186..0x12194` compares the old word at `0x2000BFCC` with the new word and checks whether `0x2000BFD2` is zero. If both conditions hold, it sets that flag to 1, calls `0x11356(0)`, then freshly loads an indirect target from `0x4005C` and calls it with `a0=uint8(0x2000BFC8)`, `a1=1`, before returning to the `0x40058` / `a1=2` / `a2=640` call at `0x11CB0`. A different word or nonzero flag routes directly to the latter call.

The same WCH V1.30 header defines `tmos_stop_task(taskID,event)` at slot 10, i.e. `0x4005C`. **If** both installed slots implement that candidate interface, the equal-word/zero-flag path can be interpreted as first requesting event 1 to stop, then requesting event 2 to start after 640 ticks. This does not prove an actual operation or time measurement, and assumes valid memory, normal `0x11356` and indirect-callee return, preserved registers and no asynchronous overwrite. The code does not thereby establish a physical button function.

### Candidate task-ID and callback connection

`0x1250A` sets `s0=0x40000`; provided intervening callees preserve it and control reaches the site, `0x1262E..0x1263C` loads an indirect target from `0x40080`, passes `0x11442`, and stores the low 8 bits of the return value at `0x2000BFC8`. Both timer calls above read that same byte. The candidate WCH V1.30 header defines slot 19 (`0x40080`) as `TMOS_ProcessEventRegister`, accepting an event callback and returning a task ID; its documentation identifies `0xFF` as an error. This supports a **conditional inference** linking the calls; it does not prove the resident version, successful registration, a valid return value, or absence of later writes to the byte.

The original `0x11442` tests bit 2 of the `a1` mask before bit 1: bit 2 calls `0x11356(1)`, clears `0x2000BFD3`, and returns the original mask XOR 2; if bit 2 is clear and bit 1 is set, it calls `0x11356(0)` and returns the original mask XOR 1. The candidate events 1 and 2 therefore align with these callback branches, conditional on compatible resident slots, scheduler and callback ABI. The control flow does not prove a particular vehicle feature or actual event execution.

### Record selection by the event branches

`0x11356` first reads `0x2000BFCC` and returns if it is zero. Only if it is nonzero and `0x2000BFC9` is zero does it scan up to 42 records at `*(GP+88)`, with a 6-byte stride. On each iteration it reloads the pointer and `0x2000BFCC` and compares the word assembled from the halfword at record offset 2 as low 16 bits and offset 4 as high 16 bits. The word shares the numeric address written by the sequence-completion path above; its contents are not guaranteed stable between reads.

For each match, input 1 to `0x11356` calls `0x155D0` with `255`; input 0 selects the unsigned byte at record offset 0 or 1 depending on whether `0x2000BFD2` is zero, passes it to `0x155D0`, then invokes indirect slot `0x40058` with `a1=16`, `a2=160`. More than one record may match. This describes only the scanning branch: nonzero `0x2000BFC9` takes a different path. Valid pointers and alignment, normal calls and register preservation, and undisturbed memory remain conditions. Actual record contents, product meaning, successful event processing and physical effects are not established.

### Cross-check against APP reset and RAM layout

The existing [APP reset analysis](../tsl9-reset-state-bootstrap-contract/README.md) checks that the word-zeroing range at `0x186EE` is `[0x20004080,0x2000C958)`. It contains `0x2000BFC8` (task-ID byte), `0x2000BFC9`, `0x2000BFCC..0x2000BFD0` (word), `0x2000BFD2` and `0x2000BFD3`. With original entry registers, valid memory, normal completion and no interference, these locations are zero at `0x186F8`. This is a local point-in-time conclusion, not proof that they remain zero at a later comparison, registration or callback.

The explicit CPU stores in the existing [clock analysis](../tsl9-clock-reset-noninterference/README.md) and the [candidate bootstrap write ranges](../tsl9-reset-state-bootstrap-contract/README.md) avoid those locations. Under non-aliasing, no IRQ/DMA/reentry or indirect side effects, normal calls, and a matching installed resident, this narrows known direct overwrites between reset and the candidate MRET. It does not prove startup, absence of later APP writes, successful registration or state at first use.

These addresses exceed the 32 KiB RAM endpoint `0x20008000` and remain below the 48 KiB endpoint `0x2000C000`. Under the contiguous mapping and no-remapping assumptions in the [CH32V208 candidate memory comparison](../tsl9-ch32v208gbu6-evidence-20261029/README.md), they fit the documented 48 and 64 KiB examples, not the 32 KiB example. These fields alone cannot distinguish 48 from 64 KiB, and are not a reading of physical option bytes, RAM ownership or capacity.

### Initial pointer for the 42 records

The little-endian word at `0x1ABB8` in the original BIN is `0x2000C30C`. `0x186BA..0x186DA` copies `[0x1AB60,0x1ABE0)` to the 128-byte GP region; if GP is reset to `0x20004000`, the copy completes normally, and no overwrite occurs, `*(GP+88)` initially equals `0x2000C30C`. With 42 records at 6 bytes each, their range is `[0x2000C30C,0x2000C408)`, entirely within the reset zeroing range `[0x20004080,0x2000C958)`.

Thus, after zeroing under those conditions, both compared halfwords in each record are zero. From this initial state, a nonzero key can match in the scanning branch only after later writes alter the records or pointer. The explicit writes in the candidate bootstrap and checked clock avoid this pointer and record range, but APP, IRQ, DMA, aliases or other indirect effects may later alter them. This does not establish actual values at the first scan or the product meaning of the records.

The initial pointer and record range exceed `0x2000C000` and remain below `0x20010000`; only under the WCH contiguous mapping and no-remapping assumptions above does the record range fit the 64 KiB example and exceed the 48 KiB example. Physical RAM options, pointer contents and validity remain unmeasured.

### Loading and fallback for the same record area

At `0x13238..0x13252`, the original APP initializer loads an indirect target from `0x4004C` and calls it with source `0x08077800`, destination `0x2000C30C`, and length 256. If the slot is the candidate copy routine, both regions are valid and the call completes, the whole 42×6-byte scan area is the first 252 bytes loaded. Then `0x13254..0x13264` checks whether destination offset 255 (`0x2000C40B`) is `0x5A` and calls `0x12F18` if not. This marker is not a full integrity check and alone does not establish the first 252 bytes are valid or identify their product function.

Fallback `0x12F18..0x12F44` calls slot `0x40048` with destination `0x2000C30C`, value 0 and length 256, writes `0x5A` at offset 255, then tail-jumps to `0x12EE6`. That writer requests a 256-byte copy to its stack through `0x4004C` and calls `0x9C0A` with `0x08077800` and the stack pointer. If the slots implement candidate fill/copy, memory is valid and there is no interference, fallback clears the scan area. Actual source contents, marker match, physical flash mapping and write success remain unverified. See the [existing NVM layout analysis](../tsl9-NVM-record-layout/README.md).

### Dispatch restrictions for action value 255

On each scan-branch match, the candidate callback for event mask `0x2` calls `0x155D0` with `255`. The function first checks bit `0x08` at offset 4 of the record pointed to by `*(GP+84)`; if set, `(255+6)&255=5 > 2` directs control to the restore/return at `0x1578C`, before the pending check or jump table. If that bit is clear, it reads the byte at `GP+358`: when nonzero it clears the byte and tail-jumps to `0x18110`, which tail-jumps to `0x1802E` with `a0=0`, `a1=3`, `a2=1`.

When both the bit and pending byte are zero, `(255-1)&255=254` exceeds the jump table's maximum index 252 and also returns via `0x1578C`; it does not take the 1–8 preliminary scheduling branch or enter the 253-entry relative jump table. These are original control flow and byte arithmetic, not proof that `255` always does nothing. Valid indirect data, no asynchronous overwrite, and normal execution remain conditions; the product meaning and physical effect of `0x1802E` are not established. See the [existing action dispatcher evidence](../../analysis/action-dispatch-2026-10-24/readme.en.md).

When the bit is clear, the pending byte is nonzero and control reaches the path normally, `0x18110` tail-jumps to `0x1802E` with `(0,3,1)`. `0x1802E..0x18056` stores `3` to byte `0x2000C928`, stores `0` to byte `0x2000C927`, skips the OR with the old word because the third argument is nonzero, stores `0` to word `0x2000C92C`, then tail-jumps to `0x17F80` with `a0=0`. These are concrete RAM writes on that special branch, not proof of physical execution, persistent final state, successful downstream action or the product meaning of the fields.

## `0x1A078` lookup output and dispatch

On the path reaching `0xCF36`, the code writes record offset 4 and freshly reads that byte `b` at `0xCF3A`. It then replaces the low nibble with `(b+1)&15`, preserves the high nibble, and uses the new low nibble as column. At `0xCF5A` it reads one byte from `0x1A078+16*effective_mode+column`, stores it at record offset 3 at `0xCF5E`, then tail-jumps without a return link to `0x12A08` at `0xCF62`. Thus column is 0–15, but the read byte remains 0–255; its product meaning and whether a value is a particular command remain unproved.

`0xCF36..0xCF62` contains no call to checksum function `0xED00`; this does not prove checksum is never recalculated, because upstream or post-tail callees may modify or process the record. The data flow assumes valid record memory, no alias/asynchronous overwrite between accesses and normal original control flow. `effective_mode` is not bounded by `&7`, and the local 1–5 values in the [mode writer analysis](../tsl9-mode-state-writer-contract/readme.en.md) are not a global bound.

### Local enable, selector and countdown branches

Original `0xCEDC..0xCEF6` first reads enable and returns without this lookup if it is zero. If enabled, it reads selector: `0xFF` goes to `0xCEFA` to read mode and countdown; selector 0 first takes `0xCF66..0xCF78` to update the selector, then follows the same mode/countdown path. Selector 1–254 updates the selector and forces this call's effective mode to 0 without taking that countdown decrement.

On the mode/countdown path, `0xCF0E..0xCF18` calculates and stores `(old_count-1)&255`. When the result is zero, `0xCF8A` clears enable but jumps back to `0xCF1E` to finish this lookup and tail transfer. Thus old_count=1 disables **subsequent** calls but does not cancel this one; old_count=0 wraps to 255 and does not trigger that clear. This local conclusion assumes valid memory, no asynchronous overwrite and normal control flow; it does not establish product countdown units, scheduling frequency, global state bounds or reachability.

### Conditional selector cycle

If enable stays nonzero, every call completes normally and no other writes intervene, an initial selector `0..254` is updated as `(old+1)%3`; after the first update it is 0, 1 or 2 and subsequently cycles `0→1→2→0`. In that stable cycle, a call with old selector 0 reads stored mode and decrements countdown; calls with old selector 1 or 2 use effective mode 0 and do not decrement countdown. Thus one decrement occurs per three **actually entered and completed calls**, provided enable is not cleared during that period.

`0xFF` follows a separate path: this function does not update selector and each entry follows stored mode/countdown. This does not establish real time, event frequency or a global selector domain; another writer, reentrancy, error, or disabling when countdown reaches zero invalidates the continuing-cycle assumptions.
