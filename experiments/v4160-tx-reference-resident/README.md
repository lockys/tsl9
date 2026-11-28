# TX with archived CCC query and event providers

This experiment replaces the earlier scripted provider returns with
**original instructions from two archived reference ROMs**. The bounded
oracle follows APP TX entry, CCC query and its lookup helper, APP packet
construction, the original tail transfer, and the reference event function.
It stops before the event function's final `JR RA`, or before an APP rejection
return. There is one continuous instruction run and one memory/register state.

A separate abstract C model reconstructs the same path and provider bodies.
Generated Windows host DLLs are compiled as C11/C++17 at `-O0`/`-O2`.
Each of the four configurations passes **1,733 cases per reference ROM**
(13,864 host cases per Python mode). Normal and optimized Python receipts
agree. All 32 registers, three complete memory arrays, final PC, query count
and the ordered logical access/checkpoint stream match.

These are **reference-backed conditional results**, not installed-resident
identification. CCC/task tables, frame/source bytes and the control word are
synthetic initial data. No original native code or hardware is executed.

## Pinned reference bindings

| Reference | Slot `0x4013C` | Lookup helper | CCC count byte | Slot `0x40050` |
| --- | --- | --- | --- | --- |
| V1.31 | `0x4B456` | `0x4B2E4` | `0x200033B5` | `0x4354A` |
| V1.40 | `0x4B4EE` | `0x4B37C` | `0x20003405` | `0x435D6` |

The harness requires the complete local carrier's pinned length/SHA-256 and
reads the two slot words from its actual bytes. It loads exactly the selected
22-byte CCC wrapper, 36-byte lookup and 64-byte event routine into the decoder,
alongside the pinned APP TX instructions. A different runtime call/transfer
target fails; the oracle does not substitute a function based on its name.
`profiles.py` records both profiles, and `source-provenance.json` retains their
archived source-map pointers and source identities. No download is required.

The three vendor compressed ports are interpreted **conditionally as Xwchc**:
CCC `2821` is `LBU A0,2(A0)`; event `1a21` is `LHU A4,0(A0)`; event `0ea1`
is `SH A1,0(A0)`. The decoder adapts the already reviewed local operand recipe.
This experiment does not establish the physical processor extension or turn
these encodings into standard floating-point instructions.

## Provider behavior established within this model

The reference CCC wrapper creates a 16-byte frame and saves only RA. Its
helper samples a global byte count, searches records at A1 in four-byte
steps, compares the leading halfword with the complete handle, and returns
the **first** matching record pointer or zero. The wrapper reads its value
byte at +2, or returns zero for no record, then restores RA/SP.

Consequently this selected provider code preserves GP, SP and S0/S1/S2/S3
on a normal, mapped run. It does not change TX's saved length/source/command
registers. An entry accepted by the APP's unsigned 1039 guard therefore stays
within the already bounded TX copy-length domain for these reference paths.
This preservation follows from the interpreted selected instructions; it
does not generalize to an unidentified installed provider or asynchronous code.

Both APP query sites load the same slot afresh. If both handles match, a
stable table that returns a non-one value is queried twice and still rejects;
a first result of exactly one chooses bank 0 immediately. A byte value of
255 is not treated as success merely because bit zero is set. Bank 1 remains
possible when only the second handle is eligible and the query returns one.

The reference event function reads a word at `0x4002420C`, writes zero there,
executes the recorded FENCE.I, and samples its task count. An ID below that
count selects a halfword through a global table pointer, ORs the requested
event mask into it, restores the word and yields A0=0. An invalid ID restores
the word and yields A0=3. No handler is invoked by this selected routine.
Normal nonalias cases set the event bit; repeated setting does not count it.
The final return instruction itself remains unexecuted, so no executable
caller destination is established by the compared RA value.

## Cases and discriminating checks

The 1,728-case matrix combines four entry lengths, six handle arrangements,
eight CCC tables, three task IDs and three task counts. Tables cover empty,
missing, byte values 0/1/2/255, duplicate matches and a later match. Five
directed cases add a 255-row search, forward source/destination overlap,
frame/header overlap, event/control-word aliasing and event/tail-slot aliasing.
There is one deterministic backing pattern, with explicit table/slot writes.

Per reference and compiler configuration, 1,485 cases reject in APP, 162
reach the event function's invalid-ID return instruction, and 86 reach its
success return instruction. Success here means the modeled event operation's
status, not observed transmission or event delivery.

Twelve causal tests retain exact examples, including these alias limits:

- If the event halfword aliases the synthetic control word, it reads zero
  after the initial word clear. The final word restore overwrites the
  intervening halfword write. A zero status does not mean that event bit
  remained set in this deliberately aliased example.
- An event halfword can alter the raw tail-slot word after its pointer was
  already loaded. The captured T1 stays unchanged. Here ORing one changes
  the pointer's low bit; it does not establish a different normalized target.
- Header/frame overlap can change restored RA. It is compared as data while
  execution stops before the final return; its destination is not followed.
- Packet/metadata writes may complete even when the subsequent event routine
  returns status three for an invalid task ID.

Five wrong C variants are compiled separately: wrong CCC value offset,
requiring a match on the last row, replacing rather than ORing the event mask,
accepting ID equal to count, and failing to restore the control word. Each
has a concrete final-state mismatch; the receipt records its first V1.31
witness. Trace-only disagreement is insufficient for these mutation checks.

## Nominal APP TX RAM evidence

`layout.py` independently reads the pinned original APP operands and loop
template. Reset configures GP=`0x20004000` and word-clears the half-open range
`[0x20004080,0x2000C958)`, covering every byte of the nominal TX interval
`[0x2000B18C,0x2000B9D8)` (2,124 bytes).

Later APP setup loads the fill pointer from slot `0x40048` and at `0x8EA6`
calls it with A0=`0x2000B18C`, A1=0 and A2=2124. The setup constant pairs,
slot-load/call bytes and reset store/stride/branches are checked directly.
This establishes static range coverage and requested parameters, conditional
on those paths executing with normal accesses. It does not establish the
installed fill provider's effects, exclusive allocation, RAM lifetime or
absence of other writers. The firmware's conditional storage remains a
diagnostic reservation rather than a recovered original object declaration.

## Memory, control and execution limits

Three distinct host byte arrays map 65,536 bytes at `0x20000000`, 512 bytes
at `0x40000`, and four bytes at `0x4002420C`. The last array is an ordinary
synthetic control word, **not actual MMIO**. FENCE.I produces only a logical
marker. This does not emulate interrupt enable/disable, cache synchronization,
hardware register side effects, privilege, timing or asynchronous interference.

Numeric addresses resolve only into those arrays. Host register/config/event
objects are separate; no physical-address cast or target function pointer is
used. Valid compared accesses are aligned and contained in one mapping.
The C implementation uses volatile byte accesses, including store readback;
logical widths do not prove native bus widths or atomicity. Invalid C faults
and interpreter exceptions have different semantics and are not equivalence
results. Code fetch uses fixed pinned bytes, so code modification is outside
the model. Intermediate registers are compared at calls/checkpoints/stops,
not after every original instruction.

The selected reference slot bindings, Xwchc interpretation, valid mappings,
fixed code and normal synchronous accesses are explicit conditions. Actual
resident identity, physical RAM/MMIO/IRQ behavior, event consumption, BLE
delivery and whole-firmware runtime integration remain unresolved.

## Reproduce offline

Use Windows x64, Python 3.10+, the existing pinned Clang/LLD 18.0.2 binaries,
the archived decoded APP and both local reference carriers. From repo root:

```sh
python -B experiments/v4160-tx-reference-resident/verify.py --tool-dir /path/to/llvm/bin
python -O -B experiments/v4160-tx-reference-resident/verify.py --tool-dir /path/to/llvm/bin
python -B experiments/v4160-tx-reference-resident/test_oracle.py
python -O -B experiments/v4160-tx-reference-resident/test_oracle.py
```

The APP must have SHA-256
`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.
Inputs and compiler/linker hashes are pinned. The host worker has a 120-second
timeout and individual build commands have 30-second limits. Only generated
host DLLs are loaded, without CRT/DLL-entry dependencies, and unloaded before
temporary cleanup. Sources are checked before/after execution without claiming
atomic filesystem snapshots. The oracle remains a bounded, adapted decoder,
not a certified emulator or independent proof of the extension semantics.

`verification.json` records both Python modes, compiler/reference profiles,
causal tests, static RAM findings and mutation witnesses. This package does
not depend on earlier scripts at runtime. The regular firmware build and its
76,800-byte reproduction milestone are unchanged and were not rebuilt here.
Analysis uses local files only; GitHub is used to publish the results.
