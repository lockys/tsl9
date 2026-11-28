# RX payload store bounds and live-order C semantics

The selected original RX payload path now has compiled C11/C++17 semantics
checked against decoded original instructions. This complements the existing
whole-ingress C model; it does not relabel that model as fully ISA-verified.

The bounded oracle starts at `0x89FA`, after payload-state dispatch and input
byte loading, and stops **before `0x897E`** advances the outer byte loop.
It includes the checksum path at `0x89A8`, the state-six update and the
over-limit state clear. Its five code ranges total **76 bytes / 24
instructions**. No clock helper, callback guard, CCC provider, router,
frame return or hardware operation executes.

Each of C11/C++17 at `-O0`/`-O2` passes **5,880 cases**: 5,040 write a payload
byte and 840 reject the sampled counter. Comparison includes all 32 final
registers, the entire 65,536-byte synthetic RAM, the stop PC and the complete
ordered abstract memory-access stream. Normal and optimized Python results
agree. Eleven causal tests pass, and seven separately compiled wrong C
variants have final-state mismatch witnesses.

## Exhaustive counter address audit

Separately from those execution cases, `layout.py` decodes the actual counter
load, unsigned comparison, branch target, PC-relative RX base, old-counter
addition and byte store. It enumerates **all 65,536 possible loaded halfword
values**, producing this exact address image:

| Old counter | Payload store at `0x8A1C` |
| --- | --- |
| 0–1039 | One byte at `0x2000B9D8 + old_counter` |
| 1040–65535 | No payload store; branch to state clear |

The fixed-base destination interval is therefore
`[0x2000B9D8,0x2000BDE8)` (1,040 bytes). This is a decode-derived finite
address calculation, **not** 65,536 executions of C or the interpreter.
It does not require assuming a valid advertised packet length or an initial
counter obtained through a complete real callback trace.

The previous nominal TX range is `[0x2000B18C,0x2000B9D8)` (2,124 bytes).
The two intervals are adjacent and nonoverlapping. Both are covered by the
original reset's configured word-clear interval. The checker also retains the
original later request to fill the TX range with zero through slot `0x40048`;
it does not infer that installed provider's effects.

With GP fixed at the original reset value `0x20004000`, the selected path's
other stores are confined to GP+138 (halfword count), GP+156 (byte state)
and GP+165 (byte checksum). Their actual instruction operands are checked,
and these stores plus the payload interval are disjoint from nominal TX.
This is a **local, conditional write-disjointness result**. It does not establish
exclusive RAM ownership, preservation of GP elsewhere, absence of other
writers, or lifetime/IRQ/DMA behavior across the firmware.

## Original order retained

For an accepted counter, the instruction sequence:

1. Loads the old unsigned halfword count at GP+138.
2. Stores its incremented low halfword back to GP+138.
3. Uses the **old** count to store the incoming A5 byte in the RX buffer.
4. Reads the expected length from GP+142 **after** that payload store.
5. Writes state six when the incremented count is greater than or equal to
   that fresh length; otherwise it leaves the state backing byte alone.
6. Reads a checksum byte through the current **S1 pointer**, adds it to A5,
   then stores only A5's low byte at GP+165.

On the rejected path, it only reads count and clears the state byte. It does
not read expected length, payload backing or the checksum pointer.

A5 retains its complete 32-bit addition result. For incoming 255 and a
checksum sample of 255 it is 510, while the stored byte is 254. One compiled
mutant produces the same memory trace but a different final A5; the full
register comparison detects it.

## Alias cases and scope

The corpus samples nine normal-GP counts, seven lengths, four incoming bytes,
two checksum initial values and five checksum pointer choices. Additional
aligned synthetic GP layouts place payload backing on the count, expected
length, state or checksum field. These are local slice-entry fixtures, not
proof that ordinary APP setup produces those layouts.

The causal tests show that a payload byte can overwrite the new count,
change the length used by the following comparison, or become the next
checksum sample. A state-six update is visible if S1 points to the state.
If checksum storage aliases payload backing, the later checksum store can
replace the byte just copied. Thus the fixed payload-store bound must not be
generalized to arbitrary GP-relative stores or universal TX/RX separation.

S1 normally comes from GP+165 earlier in the callback. Keeping it as an
explicit live register also checks the selected instructions under independent
synthetic pointer values. There is no assumption that a checksum read can be
moved earlier or replaced with a fresh calculation from GP.

Seven wrong C variants test the 1040 guard boundary, old/new destination
counter, cached expected length, early checksum sampling, equality-only state
transition, ignoring S1, and truncating the checksum register. Each has a
recorded memory/register/PC mismatch; trace-only differences are insufficient.
The exact whole-callback state, original calling convention and runtime
reachability of each fixture remain outside this experiment.

## Reproduce offline

Use Windows x64, Python 3.10+, the existing pinned Clang/LLD 18.0.2 tools and
the archived decoded APP. From repository root:

```sh
python -B experiments/v4160-rx-payload-bound/verify.py --tool-dir /path/to/llvm/bin
python -O -B experiments/v4160-rx-payload-bound/verify.py --tool-dir /path/to/llvm/bin
python -B experiments/v4160-rx-payload-bound/test_oracle.py
python -O -B experiments/v4160-rx-payload-bound/test_oracle.py
```

The APP identity is the 76,800-byte SHA-256
`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.
The harness pins tool hashes and checks source hashes before/after execution.
Generated host DLLs have no CRT/DLL-entry dependency, are unloaded before
temporary cleanup, and run in a worker with a 120-second timeout. Individual
build commands have 30-second limits. The checks do not claim an atomic
filesystem snapshot.

One synthetic RAM array maps `0x20000000..0x20010000`. Register, event and
result objects are separate host storage. Numeric addresses resolve only
into the array; there are no physical-address casts or target function calls.
Valid compared accesses are aligned and wholly mapped, and incoming A5 is
an unsigned byte. The C helper uses volatile bytes and store readback.
Logical event widths do not prove bus width, atomicity, timing or fault/trap
equivalence. Invalid C and interpreter diagnostics have different semantics.
Intermediate registers are compared at the stop, not after every instruction.

`source-provenance.json` identifies the adapted helpers/decoder/layout and
the existing ingress model used as reference. Earlier scripts are not runtime
dependencies. `verification.json` records both Python modes, actual compiled
runs, causal tests, static counter enumeration and mutation witnesses.

The regular firmware build and its existing 76,800-byte reproduction are
unchanged and were not rebuilt here. Global DATA index bounds, installed
resident identity, complete RX execution and whole-firmware runtime contracts
remain unresolved. Analysis is offline; GitHub publishes the results.
