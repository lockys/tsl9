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

## Conditional selector cycle for `0x1A078`

At `0xCEDC..0xCF96`, when the enable byte is nonzero and selector `s` is not `255`, the original code first stores `(s+1)%3`. When the old `s` is nonzero, the effective mode for this lookup is forced to 0; when old `s` is zero, it instead reads the mode byte. Old `s=255` directly reads the mode and skips that selector update. This agrees with the [full lookup contract](../tsl9-third-provider-lookup-contract/readme.en.md) and is not a global mode bound.

Provided every call enters `0xCEDC` normally, enable stays nonzero, the stored selector is not changed by callees, IRQ, DMA or aliases, and the lookup and tail call complete normally, three consecutive calls starting with `s=0` cycle old selector values `0→1→2→0`, with effective modes “current mode byte, 0, 0”. A single update from initial `s=1..254` brings the next selector into `0..2`, but `s=255` is an exception. This does not establish the conditions, three reachable calls, a stable mode or valid table data; the countdown can clear enable and make later calls return directly, so the cycle is not an observed hardware rate.

### One lookup for three specific setter branches

According to the [existing setter control-flow analysis](../tsl9-mode-state-writer-contract/readme.en.md), three branches reaching `0xD0C8` store `[enable, mode, selector, countdown] = [1, M, 0, 1]` with `M` equal to 2, 4 or 5. If that state is not changed before the next normal `0xCEDC` entry and the pointer is valid, selector first updates from 0 to 1, countdown decrements from 1 to 0, and `0xCF8E` clears enable. This call still proceeds to the lookup using `M` and a column in `0..15`, then tail-jumps to `0x12A08`. Without re-enabling, the next `0xCEDC` entry returns rather than naturally completing the three-call cycle above.

Consequently, the lookup on each of these particular setter paths falls in the existing 16-byte mode 2, 4 or 5 window. This conditional coverage does not close the complete `0x1A078` provider or prove a physical write, lookup or transmission. Other setters may supply different countdowns and selectors and an arbitrary low-byte mode; the one-shot conclusion does not apply to all entries.

#### Inputs and guards for the three branches

At `0xD07C..0xD0EC`, the entry compares the full 32-bit `a0` with byte `0x2000BF44` and returns if equal. Otherwise it calls `0x10402`, which reads `uint16(GP+80)`; a result above 8 avoids this four-byte store. When the value is at most 8, the byte at `GP+354` must also be zero before the original input saved in `s0` selects a write:

| Original 32-bit input | Written mode | Four bytes `[enable,mode,selector,countdown]` |
| --- | --- | --- |
| 1 | 5 | `[1,5,0,1]` |
| 2 | 2 | `[1,2,0,1]` |
| 4 | 4 | `[1,4,0,1]` |

On this `GP+354=0` path, other full 32-bit inputs do not perform this four-byte store. A nonzero `GP+354` instead tail-jumps to `0x10022`, described below. These are local control-flow results requiring valid GP/stack, memory and preservation of `s0`; they do not establish actual calls, exclude other writers or prove a global mode range. The [checker](check-mode-setter-guards.py) verifies the original instruction windows and the three little-endian constants without target execution or reading excluded regions.

#### Alternate record path when `GP+354` is nonzero

`0xD0DE..0xD0E8` passes the original input and `a1=0`, tail-jumping to complete function `0x10022..0x10032`. It stores the input's low byte at `GP+300` and `1` at `GP+301`; its explicit stores do not target the four-byte mode state. If both state areas have their expected non-aliasing addresses, the function itself does not change `0x2000BF38..0x2000BF3C`.

Later `0xFFA4` proceeds with a record only if both `GP+301` and `GP+354` are nonzero. It computes `(old+1)&15` from record offset 4, then ORs in the following flag selected by byte `GP+300`; other values add no flag. It stores the result at offset 4, calls `0xED00` with the record and `a1=0`, stores its returned byte at offset 3, decrements the freshly read `GP+301`, and tail-jumps to `0x12A08`.

| `GP+300` | Additional OR flag |
| --- | --- |
| 1 | `0x10` |
| 2 | `0x20` |
| 3 | `0x80` |
| 4 | `0x40` |

If no other write intervenes after setup, `0xFFA4` is reached normally and the callee returns normally, this use sees the input's low byte and decrements the single pending count from 1 to 0. This does not guarantee that a next record arrives, transmission succeeds, or a flag identifies a particular vehicle feature. Other callers of `0x10022` can supply nonzero `a1`, setting 10; the count 1 is specific to this branch.

### Observed constant arguments to the general setter

`0xD05C` turns `(a0,a1,a2)` into `[enable,mode,selector,countdown]=[1,low8(a0),low8(-a2),low8(a1)]`. The original instructions at identified direct calls or tail jumps supply the constants below; each site still has earlier guards and is not necessarily executed.

| Call site | `(mode, countdown, selector)` |
| --- | --- |
| `0xA224`, `0xE6E8` | `(3, 1, 0)` |
| `0xAC6C` | `(1, 1, 0)`, `(3, 1, 0)` or `(3, 2, 0)` |
| `0xD528` | `(5, 10, 255)` |
| `0xE1EA` | `(3, 15, 255)` |

In particular, `a2=1` becomes selector 255 through `low8(-a2)`. If the state is never overwritten and every subsequent entry and lookup completes normally, these two selector-255 paths can perform 10 or 15 lookups in mode 5 or 3 respectively; the last clears enable, so an 11th or 16th entry returns unless re-enabled. This is a conditional control-flow inference, not a measured count, rate, transmission or feature, and does not cover indirect calls or other setters.

### Guards at the two repeated-lookup call sites

`0xD50A..0xD528` first reads byte `0x2000BF44` through `0xD052`; only when it equals 1 and the byte at `GP+354` is zero does it tail-jump to the setter with `(5,10,255)`. Other conditions take other paths; these state values do not identify a vehicle feature.

`0xE1A6..0xE1EA` first requires the `GP+357` byte to be 1–4, byte `0x2000BF44` to be 4, and `0x8202` to return nonzero. `0x81B0` then loads and calls an indirect target from `0x4007C`, calculating `((x*10)&0xFFFFFFFF)>>4` from its return `x` using RV32 arithmetic. The setter receives `(3,15,255)` only if the 32-bit unsigned difference between that result and `*(GP+272)` exceeds 1999. This path subsequently writes the latest `0x81B0` result to `GP+272`; the original instructions do not add a rollover correction before comparison.

The pinned [WCH V1.30 header](https://github.com/openwch/ch32v20x/blob/ec059e0b18046b111ee850e44f105fcd095e775c/EVT/EXAM/BLE/LIB/wchble_rom.h) names slot 18 (`0x4007C`) `TMOS_GetSystemClock` with 0.625 ms units. If the installed slot matches and multiplication does not truncate at 32 bits, the `0x81B0` result can be interpreted as milliseconds rounded down. Since multiplication truncates before the shift, the difference cannot unconditionally be interpreted as physical milliseconds or timer accuracy. Slot ABI, state and real time remain unmeasured, and no product trigger is established.

#### Arithmetic witness for multiplication truncation

Let `f(x)=((x*10)&0xFFFFFFFF)>>4`. `f(429496729)=268435455`, whereas on the next tick `f(429496730)=0`. If the previously stored value is exactly the former and the slot next returns the latter input, the original 32-bit unsigned subtraction yields `4026531841`, exceeding 1999. The comparison therefore passes even if the candidate clock advanced only one 0.625 ms tick. This discontinuity comes from truncating the multiplication first; it is not the 32-bit source clock itself wrapping.

If the installed clock matches the candidate, these adjacent values are reachable, all other guards pass and stored state is undisturbed, the example supports a possible trigger at an interval different from the intuitive elapsed-time interpretation. It is an arithmetic witness derived from the instructions, not a timing measurement, proof of reachability or occurrence, or a demonstrated device defect.

#### Repetition and nine truncation boundaries

For any 32-bit `x`, the same function satisfies `f((x+2^31) mod 2^32)=f(x)`: after multiplication by 10 the difference is a multiple of `2^32`, so the low 32 bits agree. When two raw counts differ by `2^31`, their converted values are equal and their unsigned difference is zero; the result alone is not a full elapsed-time measurement. If the candidate WCH slot and its 0.625 ms tick apply, `2^31` ticks equal approximately 15.53 days. This is a conditional conversion, not a measured period.

Over raw counts `0..2^32-1` without source-counter wrap, the product crosses nine boundaries at `ceil(k×2^32/10)` for `k=1..9`; each maps adjacent converted values from `268435455` to `0`. If the saved prior value is the former, the next result is the latter and all other guards pass, the unsigned difference is `4026531841`, greater than 1999. These are arithmetic and static-instruction results; the installed slot, actual sampling, saved value, reachability and trigger remain unverified, and no device defect is established. [`check-clock-arithmetic.py`](check-clock-arithmetic.py) checks the nine boundaries and pinned instruction windows without reading excluded regions or executing the target.

### Relationship among reconstructed modes 0–5

For the six reconstructed 16-byte windows at `0x1A078..0x1A0D8` in the original BIN, each column `c=0..15` satisfies `row[m][c] = row[0][c] XOR k[m]`; `k[0..5]` are `00, E0, EF, 0F, F1, E9`. Each row's 16 bytes are distinct, so if the mode is known and one of these six rows is actually read, its output byte uniquely identifies the column within that row.

Across all 96 positions there are only 74 distinct byte values; 20 values repeat and the highest multiplicity is three. Consequently an output byte alone cannot uniquely identify both unknown mode and column. This is a reproducible relationship within one original data window, not proof of product meaning, reachability, XOR constants for other modes or the full original table extent. It must not be used to generate unknown rows or replace the `0x1A078` provider.

### An identifiable record-dispatch entry

On one dispatch-tree path from `0x14D2E`, `0x14D5E` reads record offset 0 as an unsigned halfword; if it is 553 / `0x229`, `0x14DD2` transfers to `0x150BE`. That handler calls `0xCEC0` with the record, then passes the same pointer to `0xCEDC`. The `0x1A078` lookup and record offset 3/4 changes are possible only if `0xCEC0` returns normally, saved registers and memory are preserved, enable is nonzero and the other conditions hold.

This handler also depends on the `0x829E` selection and upstream queue guards. SPI and candidate CAN1 inputs have been identified for the numerically same ring, but no particular producer or actual frame for `0x229` is established. Here `0x229` is an original dispatch comparison, insufficient by itself to identify a physical CAN ID, vehicle feature or successful transmission. The conditional CAN1 path and guards after tail-jump to `0x12A08` are described in the checksum-dispatch section of this ledger.

For the normal entry, `0x829E` directly reads byte `0x2000BFB5`; `0x14D3C` takes another exit for values above 6 and otherwise indexes the seven-entry 32-bit relative jump table at `0x1A6B8`. In the original table, index 1 points to `0x14D5E`; the other six entries point elsewhere. Thus, if control normally enters `0x14D2E`, the byte and table are stable, and the indirect jump follows the original rule, the `0x229` dispatch-tree path above requires selector byte **1**. This is not proof of a globally unique entry or actual state. The excluded `0x1A69C..0x1A6A0` data were not read.

The direct write path `0x1074C` saves incoming `a0` in `s0` and, after four original calls, writes `s0&255` to `0x2000BFB5` at `0x10766..0x10776`. That store has no 0–6 range check. This depends on prior callees returning normally and preserving `s0`; later calls and branches beginning at `0x1077A` mean the store is not the setter's only possible side effect.

`0x2000BFB5` also lies inside reset's zero range `[0x20004080,0x2000C958)`, so it is zero at `0x186F8` if zeroing completes without interference. From that state, reaching the selector-1 path above requires a later write or alias effect to change the byte to 1. These local facts do not prove `0x1074C` is its sole writer, the actual input domain, or which branch a physical record takes.

For normal dispatcher entry, when `0x829E` reads a selector greater than 6, `0x14D3C` transfers to `0x1549A`; that path restores the dispatcher frame, sets `a0=0` and tail-jumps to `0x1074C`. If those instructions and the setter's earlier calls complete normally, `s0` is preserved and there is no interference, this path writes selector 0; it also executes the setter's other calls, so it is not merely a pure byte clamp. This is one recovery path **after** an out-of-range read, not proof that all reads are 0–6, every invalid entry takes this path, or a physical device ever performed the recovery.

## Following the `0x14056` receive arguments

In the original V4.1.60 instructions, `AUIPC a2,0x20003` at `0x8A3A` and `ADDI a2,a2,-98` at `0x8A3E` compute `0x2000B9D8`. A separate PC-relative calculation at `0x8A12..0x8A1C` obtains the same base and writes a received byte at base plus counter. This supports identifying `a2` as the receive buffer; it is not a live RAM observation.

`0x89C2` and `0x89D6` construct the 16-bit length at GP+142. On the normal parsing route, `0x89E0..0x89E4` sends nonzero values above 1040 to a state-clearing path, with zero handled separately. After state and checksum comparisons at `0x8A2A..0x8A32`, `0x8A36` reloads that field into `a3`. Thus 0–1040 is conditional on normal length parsing, not a proved global invariant across all entries, alias writes, interrupts or callbacks. `a1` is the byte at GP+164; its specific command semantics are not established by that fact alone.

These observations agree with the existing [GATT receive model](../tsl9-v4160-gatt-ingress-model/README.md), which uses synthetic providers and does not establish `0x14056` internals or hardware behavior. The excluded function body was not read.

### Frame structure before the call

Along the normal state machine at `0x8962..0x8A48`, the frame starts with checks for `0x55` then `0x7F`, followed by one command byte, two length bytes assembled high-byte first, the indicated payload bytes, and finally a received checksum byte compared with the accumulator. The two prefix bytes are excluded from the sum. Starting with the command, the original code adds the command, both length bytes and the payload modulo 256. Length 0 proceeds directly to checksum; lengths 1–1040 enter the payload path, while a normally parsed length above 1040 clears the parser state.

Only after the state and checksum comparisons pass does `0x8A36..0x8A48` pass the current context, command, fixed buffer and freshly read length to `0x14056` on this path. With valid GP and buffer, no alias, inter-callback overwrite or other asynchronous interference, this supports a command/length/payload byte-sum frame interpretation. It is not cryptographic integrity, a complete command list, an authorized API or observed BLE execution, and it does not establish dispatch or side effects inside the excluded body.

#### Zero-length frame and buffer

When both normally parsed length bytes are zero, `0x89DA..0x89DE` enters the checksum state directly without the payload write at `0x8A12..0x8A1C`. The sum was cleared after the second prefix byte, so without interference the correct checksum for a zero-length frame equals its command byte. If the checksum passes, the call still receives fixed buffer `0x2000B9D8` and a freshly read length of zero; this zero-length path does not itself clear the payload buffer or establish its old contents.

The caller at `0x8A4C` clears parser state only after `0x14056` returns normally. These conclusions require state, length and buffer not to be changed by aliases, other callbacks, IRQ or DMA; they do not establish that an empty frame is reachable, that the function reads the buffer or returns successfully, or the meaning of any command. The excluded body remains unread.

#### Clock boundary during fragmented parsing

At the start of each ordinary data call, the parser obtains `now` from `0x81B0` and compares `(now - *(GP+160)) mod 2^32`; if greater than 299, `0x891A` clears parser state before storing `now` and processing that fragment. Parser state can persist across calls if this check and other memory conditions permit. `0x8900` saves this call's entry `a0` in `s3`, so the `a0` passed to `0x14056` on checksum completion is the **context of the call completing that frame**, not necessarily the context that began it.

`0x81B0` uses `f(x)=((x*10)&0xFFFFFFFF)>>4`, matching the previously documented clock truncation below. If the saved value came from `x=429496729` and the next slot value is `429496730`, the two `f` values are `268435455` and `0`; the original unsigned difference is `4026531841 > 299`, so this call clears the prior parser state. If the installed slot matches the candidate WCH 0.625 ms tick, this example spans only one tick. It does not establish a device defect or a particular frame failure: slot identity, consecutive sampling, saved state, reachability and absence of interference remain unconfirmed. Clearing state already equal to zero causes no additional state change.

The [checker](check-ingress-clock-boundary.py) reads only allowed instruction windows, directly decodes the branch at `0x8916`, and verifies nine arithmetic boundaries; it does not execute the target or read the excluded `0x14056` body.

#### Length bound under the candidate WCH write-callback ABI

The original three little-endian words at `0x19DFC` are `[0, 0x888C, 0]`. The locally preserved [WCH V1.30 header](https://github.com/openwch/ch32v20x/blob/ec059e0b18046b111ee850e44f105fcd095e775c/EVT/EXAM/BLE/LIB/wchble_rom.h) defines the second field of `gattServiceCBs_t` as a write callback and declares its `len` as `uint16_t`. If this table is actually registered under that structure, the installed firmware uses the compatible callback interface, and RV32 argument extension follows that ABI, the `a3` length at `0x888C` is **0–65535**, and the `a0` connection handle is also 0–65535.

`0x8904` saves full `a3` in `s2`; `0x8938..0x893E` compares the low 16 bits of the index against full `s2`. Under the candidate ABI, preserved loop registers and successful return from every processing step, one callback processes at most 65535 bytes and this loop does not continue because of a low-16-bit index wrap. This does not establish that actual BLE traffic reaches that length, the input buffer is valid, callees return, or the `0x14056` payload length; the latter remains subject to the normal frame's 1040-byte check and fresh-read conditions above. Other installed ABIs or entry points are not covered.

The [checker](check-gatt-callback-bound.py) reads a specified local V1.30 header and two allowed BIN windows to check the callback type, pointer table and loop branch; it downloads nothing, executes no target and does not read excluded ranges.

#### Payload write bound and reset/RAM cross-check

On each entry to the payload branch, `0x89FA` reads the counter as an unsigned halfword; `0x89FE..0x8A02` branches to the state-clear path if it exceeds 1039, before this payload store. Otherwise, `0x8A12..0x8A1C` uses the same register holding the old counter to write one byte to `0x2000B9D8+counter`. With normal instruction flow and undisturbed registers, this particular store must therefore fall in `[0x2000B9D8,0x2000BDE8)`. The local bound is independent of the length freshly read and passed to `0x14056`; it does not bound reads or writes inside the excluded callee.

This 1,040-byte window is entirely within the APP reset zero range `[0x20004080,0x2000C958)`, as are the GP-relative parser counter, length, state and checksum fields. If reset zeroing completes normally without interference, those fields and the window are zero at `0x186F8`; later reception or other paths can change them, so this does not prove the buffer is zero at a later call. Under the existing WCH candidate contiguous RAM layouts, the window falls within the 48/64 KiB numerical ranges but outside the 32 KiB range. The complete reset range itself exceeds 48 KiB, so the window alone cannot establish the overall RAM configuration. Actual mapping, boot and calls remain unverified. The [static checker](check-ingress-buffer-bound.py) checks relevant original instructions and ranges without executing the target or reading excluded regions.

Cross-checking the existing complete clock CPU-store receipt and candidate bootstrap write ranges shows that their **identified explicit write addresses** do not overlap this window or the four parser fields. If the memory mapping and installed resident contents match the candidate, both existing instruction/helper contracts hold, the clock returns normally, all loads are valid, and no MMIO-induced indirect writes, IRQ, DMA, aliasing or reentry interfere, reset's zero values conditionally persist through the analyzed bootstrap to MRET. The candidate second copy still lacks four source bytes; nonoverlapping destinations do not prove that read succeeds. This result covers neither APP execution after MRET nor state at first reception. The checker pins the two existing receipts and checks explicit write ranges only; it does not run the target.

## `0x1A69C` and settings defaults

Original `0x131A6..0x131B4` loads the indirect target freshly from `0x4004C`, passing destination `*(GP+0x54)+12`, source `0x1A69C`, and length 4. The existing [SDK copy audit](../tsl9-resident-copy-arch/readme.en.md) identifies candidate slot value `0x20000332`; its 58-byte body copies bytes forward using source, destination and length, preceded by access to `0x4002420C` and `FENCE.I`.

According to the [settings initialization analysis](../tsl9-original-prebinding-settings/readme.en.md), if reset GP and the initial pointer are not overwritten, the destination is `0x2000C2A8..0x2000C2AC`. Its initialization path checks four bytes for ASCII 32–126 and may enter the default path when a byte fails. **If** the installed slot matches the candidate, source and destination are valid, and the call returns normally, the four source bytes are copied to that destination range. This does not establish the default content, actual setting semantics, execution on every boot, or physical ROM/Flash results; excluded data was not read.

### Local constraint on the default-data destination pointer

`0x131A0..0x131B4` loads word `p` directly from `GP+84` and passes `(p+12) mod 2^32` as the destination; this slice does not first check whether `p` is zero. The candidate copy still accesses `0x4002420C` and executes `FENCE.I` before testing whether the **post-addition destination** is zero.

Thus `p=0` passes numeric destination `0x0000000C`, which is not rejected by the candidate copy's zero-destination check; `p=0xFFFFFFF4` wraps to destination 0 and causes the candidate to skip the data copy. In the former case an access to that numeric destination is attempted only if the candidate slot, source and MMIO conditions hold and control flow proceeds. This does not establish physical RAM/Flash mapping, a fault or reachability of those pointer values. Reconstruction must not equate a zero original pointer with this candidate helper's null guard. These bounds neither reveal nor infer the excluded four bytes; the [checker](check-default-copy-pointer-guard.py) pins only bounded original-call and candidate-copy instruction windows.

The initial word at `0x1ABB4` is `0x2000C29C`; with reset's GP=`0x20004000`, successful initial-data copy and no pointer overwrite, `*(GP+84)+12` is `0x2000C2A8`. When any checked byte is outside 32–126, `0x13204` calls fallback `0x1316A`: it first requests a zero fill of 112 bytes at `0x2000C29C` through slot `0x40048`, stores several fixed fields, then requests a four-byte copy from `0x1A69C` through `0x4004C`. It finally tail-jumps to `0x13138`, which requests copying 112 settings bytes to the stack and calls `0x9C0A` with numeric destination `0x08077A00`.

This fallback does not repeat the ASCII guard after the four-byte copy; without the source bytes, its result cannot be proved to satisfy 32–126. Its writer's candidate program leaf later reads 256 bytes from the stack, while this writer explicitly copies only 112 bytes; the initialization source of the remaining 144 bytes is unknown, as described in the [NVM layout analysis](../tsl9-NVM-record-layout/readme.en.md). Installed slots, valid memory and successful persistence remain unproved; excluded data were neither read nor output.

For the locally retained public WCH candidate `wchble_rom.hex` (SHA-256 `11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5`), Intel HEX record checksum checks give minimum data address `0x40000` and maximum half-open endpoint `0x6EB2C`; there are no data records in numeric interval `[0x77500,0x77B00)`. Subtracting `0x08000000` from the six settings-page operands `[0x08077500,0x08077B00)` happens to produce that interval, but **the arithmetic does not establish a hardware alias**.

This cross-check describes only record coverage in that reference HEX. It does not establish that the physical region is blank, erased, reserved or writable, fill missing candidate startup data, or prove installed ROM/Flash layout. Physical mapping and capacity require independent evidence; no device Flash was read.

## Local use of the `0x1AB48` lookup result

At `0xA146..0xA158`, the code uses `uint8(GP+176)` as an index and reads unsigned 16-bit value `x` from `0x1AB48+2*index`. On this path, `0xA15C..0xA166` computes `y=(x+0x802)&0xFFFF`; `0xA16C` writes its low 8 bits at `SP+10`, while `0xA168..0xA18E` writes bits 8–11 into the low nibble at `SP+9`, preserving its high nibble. Together these fields encode `(x+0x802)&0xFFF`. Relative to the later buffer start `a0=SP+4`, these are offset 6 and the low nibble of offset 5.

At `0xA1A8` the code calls `0xED00` with `a0=SP+4` and `a1=7`. The complete function initializes its sum from the first two buffer bytes, adds data starting at offset 3 for the byte length at offset 2, skips data index 7 and retains the low 8 bits. At `0xA1AC` the returned byte is stored to `SP+14`, which is buffer offset 10 / data index 7, then `0xA1B2` calls `0x12A08`. With a valid buffer, no interference and normal completion, this supports interpreting the result as an additive checksum; it does not establish protocol, units, actual transmission or product feature. See the [existing checksum comparison](../tsl9-feature-callback/readme.en.md).

This is static data flow for the lookup path, conditional on valid pointers and stack, no alias/asynchronous overwrite and normal callee execution. The index and resulting field have conservative byte and 12-bit widths respectively; neither proves the global index is 0–3 or that four entries constitute the complete table.

### Source byte triggering a counter update

`0x81F8` reads an unsigned byte at PC-relative address `0x2000BEEA`. At `0xA0E2..0xA0FA`, if it differs from the saved byte at `GP+170`, the code first stores the new value there and then sets `GP+176` to `(old+1)&3`. When equal it branches elsewhere and does not perform this update. The source has only the conservative byte-width range; its address or value does not establish product meaning, and other writers are not excluded.

`0x2000BEEA`, `GP+170` and `GP+176` are all in the checked reset zero range. If reset completed, GP is `0x20004000`, no other path has changed the saved value or counter before this comparison, and no interference occurs during it, those two values start at zero. The source byte may change after reset: an observed zero does not increment here; an observed nonzero value causes this update to set the counter to 1. This constrains only this local update, not whether a later lookup occurs, whether the counter stays unchanged afterward or whether its global index is always 0–3. The [checker](check-counter-source-byte.py) pins original instruction windows and address arithmetic without target execution or excluded-region reads.

#### Two identified writes to the source

On reaching `0xAF4C`, the original code reads byte `b` at input record offset 8 and computes `n=(b>>2)&15`. Its test `((n+13)&15)<=4` is exactly equivalent to `n` being 3, 4, 5, 6 or 7. On the passing branch, after two calls it freshly reads `0x2000BEEA`: if zero, `0xAF76` sets it to 1; if nonzero, this site leaves it unchanged. On the failing branch `0xB016` freshly reads the same byte and `0xB026` clears it if nonzero; an existing zero is left unchanged.

If the source is initially 0/1, input and memory are valid, the two calls return normally and no other write intervenes, these branches locally leave 1/0 respectively. If the passing branch sees an initial value of 2–255, it retains that nonzero value; this slice is not a Boolean normalizer for arbitrary bytes. These are narrow direct-address findings, not proof that indirect pointers, other encodings or asynchronous writers are absent. The field's product meaning and global index range remain unproved. The checker pins both instruction windows and enumerates the arithmetic condition for all 256 input bytes without target execution.

#### Two identified record-dispatch entries

At the normal `0x14D2E` entry, selector byte 1 directs the original relative jump table to `0x14D5E`, which reads an unsigned 16-bit value from record offset 0. In that dispatch tree, `0x0399` (921) leads to `0x152DC → 0xB036`, while `0x039B` (923) leads to `0x152E8 → 0xB05C`. Both wrappers first call `0x1069E`, which calls `0xED00` with the record and index 7 and compares the result with the byte at record offset 10. Only an equal result makes the wrapper continue and tail-jump to `0xAE0E`.

`0xAE0E` retains the record pointer. For `0x039B`, it branches at `0xAE54` toward `0xAF4C`; for `0x0399`, offset 11 unequal to 1 also goes there, whereas offset 11 equal to 1 first enters different processing and cannot be assumed to update the source byte. These observations require a valid selector, record, dynamic length and stack; normal checksum/helper returns; preserved registers; and undisturbed memory. The two numbers are **comparisons inside the record**, not by themselves proof of physical CAN IDs, a source interface or particular vehicle functions. Other entries are not excluded. The [checker](check-counter-record-entry.py) pins bounded original instructions and the allowed table entry without executing the target.

#### Conditional connection to candidate CAN1 reception

Original `0x12C24..0x12C4A` calls receive helper `0x18D78` with numeric base `0x40006400`, then passes the receive structure's low halfword at offset 0, length and data to ring insertion. Under the [WCH CAN definitions](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32v20x_can.h) and the checked helper, when identifier-type bit 2 is zero, offset 0 is formed from the receive register shifted right by 21 as the standard identifier field; `0x399` and `0x39B` both fit its 11-bit numerical range. This supports a **possible** CAN1 standard-format source for the record dispatch, not proof of observed physical frames or product semantics.

For such a candidate receive with length exactly 8, if repeated mailbox reads are coherent, a ring slot is available, candidate copy completes, consumer and other guards pass, and the record remains unchanged, record offsets 8 and 10 correspond to data bytes 5 and 7 and offset 11 has tag 0. The checksum gate then requires `data[7] == (ID low byte + ID high byte + data[0] + … + data[6]) & 255`; tag 0 also avoids the `0x399` tag-1 special branch above. This is conditional data-flow reasoning, not an observed packet or proof of queue delivery, physical wiring or vehicle action.

The extended-identifier branch writes the numeric value to receive-structure offset 4; the checked helper does not write offset 0 on that branch, although the IRQ subsequently reads offset 0. The standard-ID conclusion cannot be applied directly to extended format or assume that field was initialized. The [checker](check-counter-can1-source.py) pins allowed original instruction windows without target execution or excluded-region reads.

### Two branches that do not read the counter table

`0xA132` calls `0x81EE`, which directly reads byte `0x2000BED5`. At `0xA136..0xA158`, return value 1 selects the constant `1960` (`0x7A8`) for the common packet-field path; value 2 selects `2140` (`0x85C`) at `0xA1FC` before joining that path. Only other byte values read `GP+176` and look up `0x1AB48` at this entry, so the two fixed-value branches do not depend on that table or counter.

Given valid memory, normal return, no interference and completion of the later field logic, the low 12 bits of the constants are `0x7A8` and `0x85C`. This does not establish reachability of states 1/2, their product meanings, absence of lookups at other entry points or resolution of downstream dependencies; the complete provider cannot be removed on this basis.

### Results for the four reconstructed counter entries

The original BIN's four little-endian halfwords at `0x1AB48..0x1AB50` match the [curated data source](../../src/native/receive/input_counter_data.c). When the counter at this read is actually 0–3 and the call and memory conditions hold, the combined field `(x+0x802)&0xFFF` produced by `0xA158..0xA18E` is:

| Counter | Original halfword `x` | 12-bit field |
| --- | --- | --- |
| 0 | `0x0096` | `0x898` |
| 1 | `0x00B4` | `0x8B6` |
| 2 | `0xFF6A` | `0x76C` |
| 3 | `0xFF4C` | `0x74E` |

The final two entries are loaded as unsigned halfwords; the table reports original bits and actual low-12-bit arithmetic only, not a signed physical quantity, unit or vehicle feature. These four conditional entries do not prove other indices unreachable or resolve the provider.

### The 12-bit input guard before lookup

Original `0xA114..0xA12E` constructs 12-bit `v` from the current stack record as `((low nibble of SP+9)<<8) | *(SP+10)`. It calculates `(v-1961)&0xFFFF` and branches to `0xA1E8` if that unsigned result exceeds 178, bypassing this `0xA132` state selection and the `0x1AB48` lookup. Because `v` itself is 12-bit, the exact values passing this guard are **1961–2139 inclusive**. Other upstream conditions still apply; not every record in that range is established to reach the lookup.

The four conditional outputs above are 2200, 2230, 1900 and 1870; the two fixed outputs from the non-lookup branches are 1960 and 2140. All six lie outside this input guard. If a later input record happens to re-enter this guard with the same two fields unchanged, it bypasses this lookup path. This conditional field relationship does not prove a record is fed back, a physical feedback loop exists, or any particular product feature. The [checker](check-counter-input-guard.py) verifies the relevant instruction window, the four allowed data entries and arithmetic for all 4,096 possible inputs offline, without target execution or excluded-region reads.

These values have a reproducible symmetry around `0x802` (2050): accepted inputs are `2050±89`, the two fixed outputs are `2050±90`, and the four conditional table outputs are `2050±150` and `2050±180`. This is arithmetic on a 12-bit field, not proof of a neutral position, physical units or a particular control function. The checker decodes all four halfwords directly from the eight allowed original data bytes before verifying these relationships.

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

### Distinguishing the four pattern pairs

The 48 original bytes at `0x1A638..0x1A668` match the [reconstructed data](../../src/native/receive/sequence_pattern_data.c). For each channel, the state 0/1 six-byte patterns begin `02 00`/`03 00` and share their last four bytes; those four-byte suffixes differ across all four channels. Thus, provided state is 0/1, the candidate `0x4003C` six-byte equality contract holds and input remains stable, all eight patterns are pairwise distinct and the same six-byte input cannot match two groups at once.

Specifically, if all four states begin at 0 and two successive inputs satisfying the length-byte-6 / second-data-byte-zero guards exactly match one channel's state 0 then state 1 patterns, with comparison and memory undisturbed between calls, the first sets that channel to 1; the second resets it to 0 and enters the marker path at `0x1207A`. This does not cover arbitrary interleaving or unknown initial state and does not establish that the device received these inputs, the meaning of the other marker-word bytes or any physical button function.

#### Ordering of two interleaved groups

Assume the eight patterns above are distinct, all four states start at 0, the comparison slot matches the candidate contract, all three inputs reach this loop and no interference occurs. Let `A0`/`A1` be channel A's state 0/1 patterns and `B0` another channel B's state 0 pattern. The result of `A0 → B0 → A1` depends on loop order:

| A and B order | Effect on A during `B0` | Conditional result during `A1` |
| --- | --- | --- |
| `B < A` | B matches and exits first; A is not checked and retains state 1 | B first mismatches and clears; A matches and enters the marker path |
| `A < B` | A first mismatches and clears, then B matches | A's state 0 pattern differs from `A1`; all eight patterns are distinct, so no match marker is produced |

This is conditional reasoning from the loop's current-state reset on mismatch, immediate exit on its first match and the existing data. It is not an observed BLE message or vehicle action, and does not cover unknown states or other inputs. The [checker](check-sequence-interleave.py) pins only the original instruction and allowed 48-byte data windows; no target, host model or ISA is executed.

### Upstream of the six-byte comparison input

On the branch where bit 15 of incoming `a1`'s low 16 bits is set, original callback `0x119C8` loads and calls an indirect target from `0x4006C`; only a nonzero returned pointer with byte `0xB0` at offset 0 proceeds into the relevant message processing. The pinned [WCH V1.30 header](https://github.com/openwch/ch32v20x/blob/ec059e0b18046b111ee850e44f105fcd095e775c/EVT/EXAM/BLE/LIB/wchble_rom.h) defines this slot 14 as candidate `tmos_msg_receive(taskID)`. That supports a queued-message interpretation, but does not prove the installed slot, message origin or complete ABI.

The original path first compares the halfword at message offset 2 against three candidate values. For message offset 4 equal to 27 or 29, it compares six bytes at `*(GP+92)+43*i+3` with a selected state area via `0x4003C`, for at most three entries. After a match and other guards, `0x12392` loads the word at message offset 12 into `s3` as the data pointer, and `0x12396` loads the byte at offset 10 into `s4` as the length. It calls `0x838E` with that pointer and length, requiring zero, and must pass additional indirect comparisons and branches before it can reach `0x12020`, which checks length 6 and data byte 1 equal to zero.

This is a conditional static structure requiring valid pointers, installed indirect-function contracts, preserved registers and no asynchronous overwrite. It does not establish a physical BLE message, data lifetime, product meaning of the numeric message fields or all reachable paths. No user-device data was read and no callback was executed.

### Candidate WCH GATT event layout

The same pinned WCH header defines `0xB0` as `GATT_MSG_EVENT`, 27 / `0x1B` as `ATT_HANDLE_VALUE_NOTI` and 29 / `0x1D` as `ATT_HANDLE_VALUE_IND`. Its `gattMsgEvent_t` contains an event header, `connHandle`, `method` and a message union. The candidate notification/indication structure has `uint16_t handle`, `uint16_t len` and `uint8_t *pValue`.

If the installed device uses that structure with RV32 little-endian and ordinary 4-byte pointer/union alignment, the header, connection handle, method and union lie at offsets 0, 2, 4 and 8. For the notification/indication union members, handle, 16-bit length and pointer lie at message offsets 8, 10 and 12. This agrees with the original numeric accesses and method branches, supporting a **conditional inference** that the input is GATT notification/indication data, not proof of the installed ABI or an observed BLE packet.

In particular, `0x12396` uses `LBU` and reads only the byte at offset 10; even if the candidate structure's `len` is 16-bit, that instruction does not examine its high byte. Thus `s4==6` establishes only that the byte read is 6; the guard alone does not prove the full 16-bit length is 6. Actual readable buffer extent, earlier validation and installed ABI require additional evidence.

At `0x123A4`, the code first passes that pointer and the length byte read to `0x838E`; this function is not a pure predicate. It checks two positions at a 4-byte stride from `0x2000C794`: when the corresponding halfword is not `0xFFFE`, a type byte equals 2 and another byte is nonzero, it caps the passed length at 30, requests a copy to stack+2 through slot `0x4004C`, then calls `0x8A56` with the data including a two-byte prefix. The numeric field views overlap; they do not by themselves establish a C structure or ownership.

`0x123A8` continues toward the later pattern comparisons only when `0x838E` returns 0; a nonzero byte from a matching entry is among that function's return values. This is static evidence of conditional prior processing and continuation on zero, not proof that `0x8A56` transmits successfully, actual record contents, null/length safety or installed slot identity. The copy and later effects still require valid buffers, normal callees and no interference. See the [existing function evidence](../../analysis/callback-completion-2026-10-25/readme.en.md).

### Callback registration and message lifetime

At initialization `0x1253C..0x12550`, the original code loads an indirect target from `0x40080`, passes `0x119C8`, and stores the low byte of the result at `0x2000BFD4`. If the installed slot matches the same header's `TMOS_ProcessEventRegister`, this can be interpreted as registering the callback and saving a task ID; `0xFF` is the candidate interface's failure value and the original instructions do not check the result there. Actual registration success, later overwrites and scheduler ABI remain unknown.

At common cleanup `0x1240C`, a `0xB0` message causes the code to pass `message+8` and `message[4]` to slot `0x4012C`, then at `0x1241E` passes the message to `0x40068`. A non-null non-`0xB0` message goes directly to the latter; a null pointer skips both. The candidate WCH header names slots 62 and 13 `GATT_bm_free(gattMsg_t*,opcode)` and `tmos_msg_deallocate(msg_ptr)` respectively, and its candidate `gattMsg_t` union and method offsets match these operands.

If the installed slots match those candidate interfaces, both calls return normally and memory is valid, this supports processing the GATT inner buffer before freeing the outer message. The data referenced by `message+12` cannot be assumed valid after this cleanup without separate ownership evidence. Installed slots, successful release, all other exits and pointer aliases are unproved; no device code was executed.

### Sources for the three six-byte comparisons

The reset seed's word at original BIN address `0x1ABBC` is `0x2000C40C`. With GP=`0x20004000`, the initial copy completed and no overwrite, `*(GP+92)` points there. The `0x11A58..0x11A76` loop uses offsets 0, 43 and 86, comparing six bytes at pointer plus offset plus 3. Its three half-open windows are `[0x2000C40F,0x2000C415)`, `[0x2000C43A,0x2000C440)` and `[0x2000C465,0x2000C46B)`.

`0x132C8..0x132F8` requests a 133-byte copy from numeric source `0x08077500` to `0x2000C40C` through slot `0x4004C`, then checks for marker `0x5A` at offset 132; all three windows lie inside the loaded region. If the slot is the candidate copy, pointers and memory are valid and remain unchanged, this connects the comparisons to that candidate settings region. The marker is not a full integrity check, and actual source contents, identity meaning and physical Flash mapping are unknown.

On marker mismatch, `0x13108` requests filling 133 bytes with zero via `0x40048`, writes `0x5A` at offset 132, then tail-jumps to writer `0x130D6`. If the fill contract and other conditions hold, the three comparison windows are cleared; actual matching, later reconfiguration and successful writes remain unproved. No device connection identifiers were read or output. See the [NVM layout analysis](../tsl9-NVM-record-layout/readme.en.md) for the numeric source and 133-byte writer boundaries.

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

#### Cleared records and the sequence-completion marker

If that fallback's candidate fill clears 256 bytes normally and only offset 255 is subsequently written to `0x5A`, the first 252 bytes used by the 42 records remain zero, so each comparison word assembled from record halfwords at offsets 2 and 4 is zero. By contrast, the normal four-channel completion marker at `0x1207A..0x1209A` has low byte `0x80..0x83` and is therefore nonzero.

If the record pointer still targets this region, the completion marker remains at `0x2000BFCC`, `0x2000BFC9=0`, memory accesses and calls complete normally, and no other write or asynchronous interference occurs, this `0x11356` scan cannot match any of the 42 records and cannot call `0x155D0` through its match branch. Other calls to `0x155D0` are not excluded; fallback, sequence completion, timer events and physical actions are not established, and actual settings may contain nonzero records. The [checker](check-sequence-cleared-records.py) pins three original instruction windows without reading device data or executing the target.

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

### Fixed CAN filter table limits the proposed receive source

`0x12B82` calls `0x1299E`, which copies 96 bytes from `0x19CA8` and passes them to `0x128FE`. The original table contains 48 little-endian 16-bit values, all at most `0x7FF`, with no `0x399` or `0x39B`. The [checker](check-counter-can1-fixed-filters.py) pins the original instruction and data windows and checks the two left-shifted encodings without executing the target.

After calling two resident slots whose contracts are unconfirmed, `0x128FE` processes 14 groups of four halfwords, shifts each left by five and calls `0x18BA2`. If those slots correctly zero 112 bytes and copy 96 bytes respectively, the remaining eight values are zero. Under the preserved WCH CAN definitions, this path configures 14 enabled 16-bit ID-list banks for FIFO0. If configuration succeeds, the hardware uses the corresponding standard-data-frame matching semantics, and no subsequent write changes it, this fixed table does not accept IDs `0x399` or `0x39B`. This constrains the earlier CAN1 source inference; it does not establish that the device uses this configuration or exclude other configurations, external controllers or other sources. Actual resident behavior, effective filtering and device traffic remain unverified.

The **first** copy of the fixed table can be narrowed using APP instructions: `0x1299E` calls the complete local routine `0x19BF0..0x19CA6` with source `0x19CA8`, length 96 and current `SP` as destination, then passes that same `SP` and length 96 to `0x128FE`. The source address is four-byte aligned. If the destination is also aligned, both ranges are valid and non-overlapping, addresses do not wrap, and no interference occurs, original `0x19C3C..0x19C9C` copies two groups of 36 bytes, then six words for the remaining 24 bytes, exactly 96 bytes. With an unaligned destination and aligned source it instead takes the byte-copy path, also ending at destination plus 96.

Under those memory and control-flow conditions, the source passed to `0x128FE` contains the 96-byte fixed table. This does not resolve the **second** copy's `0x40048`/`0x4004C` resident contracts or prove that the actual filter is configured or remains unchanged. The [branch checker](check-key-control-flow.py) verifies the two calls and key local-copy branches and strides; the arithmetic is not hardware or target execution.

#### Two candidate SPI channels on the same branch

After the fixed table setup returns, the same `0x12B82` branch calls `0x16DD4` with channels `1` and `2` in turn. That function clears two stack words, then stores `0x01450399` for channel 1 or `0x039B0370` for channel 2 and calls `0x16CC4` with length 8 and `a3=1`. In little-endian halfwords, the first four entries are `[0x399, 0x145, 0, 0]` and `[0x370, 0x39B, 0, 0]`, respectively.

If the two resident slots actually zero 12 bytes and copy 8 bytes, required registers survive calls, and all six iterations finish, `0x16CC4` supplies these four entries plus two zero entries as 11-bit candidate filter values to the SPI write path. The candidate receive path at `0x16A7C..0x16AFA` passes the decoded ID and original channel as the ring record ID and tag. If all 13 SPI reads, data format, memory and ring operations satisfy their conditions, channel 1 ID `0x399` can form tag 1 and channel 2 ID `0x39B` can form tag 2. The former encounters the `0x399` tag 1 special branch described above, so the CAN1 tag 0 conclusion does not apply.

This is a static link between initialization and receive data flow, not proof of actual controller identity, masks or effective filtering, received packets, checksum success or downstream state changes. Channel numbers are labels, not established physical wiring. The [checker](check-counter-spi-filter-path.py) pins original instruction windows and verifies constant encoding without executing the target.

#### Candidate EXTI, SPI selection and record tag

The existing [vector comparison](../tsl9-qingke-v4-vectors/readme.en.md) maps slot 39 to `0x16FB6`; under the candidate WCH CH32V208 definition it is EXTI9_5. That routine reads bits 6 and 7 of `0x40010414`, writes `0x40` and `0x80` respectively to the same address, and sets bits 0 and 1 of `GP+360` respectively. The locally preserved [WCH header](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32v20x.h) identifies that address as the EXTI interrupt-pending register and those bits as lines 6 and 7; actual mapping and clear effects remain unverified.

If `0x17002` is subsequently entered, flags remain valid and intervening calls preserve required registers, bit 0 calls `0x16B0A(1)` and bit 1 calls `0x16B0A(2)`; the second flag is freshly read, so simultaneous observation cannot be assumed. `0x16B0A` reads candidate SPI device register `0x2C` and, according to bits 0 and 1 of the result, calls `0x16A7C` with addresses `0x61` and `0x71`. The receive function writes `0x10` to `0x40010814` for channel 1 and `0x01` for channel 2; under WCH GPIOA mapping and active-low wiring these are candidate PA4 and PA0 chip selects. Once header and length guards pass it passes the original channel to `0x12BC8`; with a free ring slot, valid copy and preserved registers, the corresponding record tag is 1 or 2.

This supplies a concrete candidate source for `0x399`/`0x39B` only if initialization, IRQ delivery, SPI device and data format are all compatible. It does not establish actual PCB wiring, receipt of a particular ID or a counter change. See the [independent instruction checker](check-key-control-flow.py); no hardware or firmware was executed.

#### EXTI line 6/7 initialization instructions

`0x170A2..0x170F4` calls the existing GPIO helper `0x9A24` with `(0x40011000,0x40,0x48)` and `(0x40011000,0x80,0x48)`. Under the checked WCH definitions and helper contract this requests **PC6/PC7 as pull-up inputs**. Then `0x17104` and `0x17112` call local helper `0x1904A` with `(2,6)` and `(2,7)`. The helper performs read-modify-write on four-bit fields of `0x4001000C`; under the WCH AFIO mapping and unchanged arguments it sets both fields to 2, selecting GPIOC as the source of EXTI 6/7.

The same initialization prepares `[line=0xC0, mode=0, trigger=12, enable=1]` on the stack and calls `0x18E1C`. The complete helper clears `0xC0` bits in `0x40010408`, sets them in `0x4001040C`, and sets them in `0x40010400`. Under WCH EXTI definitions this disables rising edges and enables falling edges and interrupts for lines 6/7. These steps statically correspond to the candidate EXTI handler's bits 6/7 and the two SPI channels.

This depends on a valid stack, normal calls, preserved registers, no remapping or asynchronous overwrite, and the candidate WCH register definitions. It does not measure actual pin levels, establish PCB continuity to the controllers, prove IRQ delivery, or exclude later reconfiguration. The [independent checker](check-key-control-flow.py) pins initialization and both helper instruction windows.

#### Conditional interaction of startup order and flag clearing

Original APP main calls IRQ initializer `0x9A42` at `0x9258`; that routine writes the EXTI9_5 mask to the candidate PFIC enable address at `0x9ABE` and sets the global-interrupt-related CSR mask at `0x9AC2`. Only after other initialization calls does main invoke PC6/PC7 initializer `0x17040` at `0x9280`. On entry, `0x17048..0x17058` requests a zero fill of the three bytes `GP+360..362` through slot `0x40048`; the GPIO and EXTI configuration described above comes later.

If the slot satisfies the candidate fill contract, memory is valid, and after the early enable request but before this fill completes the candidate EXTI handler runs due to pre-existing pending/enable conditions and sets bit 0 or 1 of `GP+360`, the fill can clear that already-set flag. This is a specific **possible ordering**, not a measured race: early peripheral enable/pending, actual IRQ delivery, installed slot contents, and whether a cleared event was observable are not established; other initializers may also affect state. Normal return from intervening calls including `0x14C8A` is a condition. The excluded region was not read.

#### Main-loop order for receive flags and queue

`0x900C` calls initializer `0x9250` and, after normal return, `0x900E` calls `0x8180`. Its loop loads an indirect target from numeric address `0x20000000` and calls it, calls flag consumer `0x17002` at `0x819E`, calls queue consumer `0x12C58` at `0x81A2`, then jumps back at `0x81A8`. The candidate WCH bootstrap stores `0x200007D0` at `0x20000000`, but the installed slot and ABI are unconfirmed.

If initialization and the indirect call return normally, the corresponding flag is set when consumed, receive successfully inserts a queue record, and calls and memory remain valid, the **same normal loop iteration** next enters `0x12C58` to scan the queue. Whether it finds that slot, passes guards or enters `0x14D2E` depends on later conditions. This links candidate EXTI/SPI receive to the counter-record dispatch without proving actual packets, loop execution, timing or product functionality.

#### Convergence of the `0x399`, tag 1 special branch

If the upstream checksum and other guards pass and control reaches `0xAE62`, this branch asks the slot at `0x4004C` to copy the original 12-byte record to `SP+4`. If the slot is a forward copy and both ranges are valid, `SP+12` initially corresponds to original record offset 8. This branch may modify **the stack copy** at `SP+12`, recalculate the copy's checksum and call `0x12A08`; none of that proves successful transmission.

Tracing all static branches in `0xAE70..0xAF4C`, `s2=0` at `0xAF48` falls through to `0xAF4C`; `s2≠0` first goes to `0xAEE0` to process the copy and, after checksum and `0x12A08` return, jumps to the same location at `0xAF08`. Other branches converge through these paths. **If** all traversed direct and indirect calls return normally, saved `s0` and stack remain valid, and no alias or asynchronous interference occurs, the tag 1 special branch can still reach `0xAF4C`. That location freshly reads `s0+8` from the original record, not the stack copy. Therefore its counter-source condition still uses whether `(b>>2)&15` from the original byte is 3–7; the modified copy byte cannot be substituted.

This establishes conditional control flow and data provenance, not actual packets, initial checksum success, callee side effects, stable memory or a counter update. The [checker](check-counter-tag1-convergence.py) pins relevant original instruction windows without executing the target or reading excluded ranges.

### Guards on the second counter writer

Within `0xA2EE..0xA37C`, the `(old+1)&3` store at `0xA344` occurs only on a guarded path. First, the byte returned by `0x829E` must be 1; otherwise the function tail-jumps to `0x10816` without this store. Then `0x81DE` reads offset 5 of the region pointed to by `*(GP+84)` and returns `(byte&3)+1`. If bit 0 of that return is 1, the code first calls `0xA204`; it continues only if bit 1 of the saved return is 1. Across all four low-bit combinations, the latter requires the original byte's low two bits to be **1 or 2**.

Reaching `0xA344` additionally requires nonzero return from `0x821E(2)`, nonzero full entry `a0`, and a freshly read configuration offset 3 low nibble **not equal to `0xF`**: `0xA32E` is `beq a5,a4,0xA372`, and equality exits. This corrects the previously reversed branch interpretation. Assuming valid pointers and memory, normal calls, preserved saved registers and no asynchronous or alias interference, the code increments the counter, sets `GP+175` to 1, and tail-jumps to `0x9124` with callback `0x9F74` and `a2=(entry a0 × 1000) mod 2^32`. The body of `0x9F74` clears `GP+175`; at `0xA1E2`, a nonzero byte can branch to the field guard at `0xA114`. This does not prove callback registration, execution or later lookup reachability.

When bit 0 of `0x81DE`'s result is 1, `0xA204` has additional effects, so the low-bit condition alone is insufficient. These are necessary local conditions, not global state limits, and other counter writers are not excluded. The [checker](check-counter-second-writer.py) pins the original instruction windows and checks all four low-bit combinations without executing the target.

#### Input and timer conversion at the identified caller

At the identified direct call `0x172FC`, upstream `0x172CA` takes the low four bits of configuration offset 8, yielding 0–15; only when offset 3's low nibble is `0xF` and `0x829E` returns 1 is it capped at 3. If configuration remains consistent across the two checks, reaching `0xA344` requires offset 3's low nibble not to be `0xF`, so the cap-to-3 branch is **not taken**. With preserved registers and an actually reached store, the nonzero input is **1–15**. The earlier 1–3 claim was wrong. Other indirect calls and changing memory require separate analysis.

Under those conditions, for input `n=1..15`, `0xA360` passes `a2=1000*n` and `a1=0` to `0x9124`. If the scheduler finds an existing matching entry or a free entry and calls and saved registers remain valid, `0x91D0..0x91E8` multiplies by 1000 and divides by 625, yielding **1600*n**, without overflow in this range. `0x922C` loads the indirect target from `0x40058`; if it matches the WCH V1.30 `tmos_start_task` interface and 625-microsecond tick, the nominal delay is **1–15 seconds**.

An available scheduler entry, actual slot identity, successful call, timer accuracy and callback execution are not established; the 1–15 conclusion does not apply to other callers. The [checker](check-counter-caller-delay.py) pins instruction windows, directly decodes both branch instructions, operands and targets, and checks arithmetic for 1–15 without executing the target.

#### Scheduler capacity versus callback execution

For nonzero delay, APP `0x9124` scans a 15-entry table with 12-byte stride for a matching callback word at offset 4, then scans for a free entry only if no match is found. If all 15 callback words are nonzero and none is `0x9F74`, with no asynchronous mutation and normal control flow, both scans finish at `0x924C` and return 1 without this attempt calling the timer slot at `0x40058`. The preceding `0xA344` path has already updated the counter and set `GP+175` to 1; this scheduler failure path does not undo those stores. With no other writer or asynchronous interference, the flag remains 1, so the counter update alone does not establish successful timer creation.

Conversely, original `0x907A..0x90AC` requests that the 180-byte work table be cleared, passes `0x901A` through slot `0x40080`, and stores the low returned byte at `GP+166`. `0x901A..0x907A` selects a slot using an event bit; when the slot's byte flag is 0, it clears the callback and argument words before calling the saved callback with the argument. If this initialization, the preceding one-shot schedule, the candidate WCH event interface and event delivery all succeed and the slot is unchanged, saved `0x9F74` can clear `GP+175`. This does not establish actual registration, timer startup, event delivery or a permanent flag value. The [checker](check-counter-scheduler-capacity.py) pins relevant instruction windows without executing the target.

## Independent audit of recent branches

Following the earlier `0xA32E` branch-direction error, the [static checker](check-key-control-flow.py) reads **only twenty explicit windows** from the original BIN, validates their hashes, places each in radare2 temporary memory for RISC-V disassembly, and checks 76 selected instructions. It covers counter, selector, sequence state, fixed-filter table copying, and candidate EXTI/SPI receive, main-loop and initialization paths. A negative check changes a branch bit in temporary memory; the original BIN is not modified.

Run `python experiments/tsl9-six-dependency-ledger/check-key-control-flow.py --r2 /path/to/r2`. On Windows, provide the local path to `r2.exe`; an existing radare2 with RV32C support is required and the checker downloads nothing. This audit confirms the listed instructions and destinations; it does **not** prove the semantics of other instructions, dynamic reachability, callee contracts or hardware effects. It does not read excluded ranges, execute the target or run an emulator.
