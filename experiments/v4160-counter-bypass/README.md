# Counter lookup: post-copy bypass and conditional index origins

The counter read at `0xA158` does not have a local `&3` bound. This experiment
now checks the actual bypass with compiled C and continuous decoding of
original APP instructions, including both small APP getters. It narrows the
earlier CFG-only observation without claiming a global counter invariant.

The snapshot starts at **`0xA0E2`, after the copy call at `0xA0E0`**. It does
not execute the preceding copy, reconstruct its return contract or establish
a complete normal-entry path from `0xA054`. The selected decoder covers
186 bytes / 59 instructions, using one register array and one memory state.

Each of C11/C++17 at `-O0`/`-O2` passes **3,600 snapshot cases**. All 32 final
registers, complete synthetic RAM and the selected eight Flash DATA bytes,
the stop PC, getter count, analysis-window diagnostic and ordered abstract
access/call snapshots agree. Normal and optimized Python results match.
Ten causal tests pass; seven separately compiled wrong C variants have
final-state mismatch witnesses.

## The bypass in original instructions

1. The actual getter `0x81F8` reads the byte at `0x2000BEEA`. The caller
   compares that complete byte with the cached byte at GP+170.
2. If they differ, the caller updates GP+170, reads GP+176 and stores
   `(old_counter+1)&3`. It then reaches a registration or cancellation call;
   this experiment stops **before** that call executes.
3. If the bytes are equal and nonzero, `0xA0EA → 0xA1F6 → 0xA114` bypasses
   the counter write. If they are both zero, the path instead reads GP+175
   and continues only if that byte is nonzero.
4. The packet-field gate accepts only `1961..2139`: the original checks
   `u16(field−1961) <= 178`. Then the actual getter at `0x81EE` reads the
   byte at `0x2000BED5`.
5. Getter result one selects numeric value 1960; result two selects 2140.
   Other results read the current counter at GP+176 and form
   `0x1AB48 + 2*counter`, with **no index mask or intervening call**.

The getters are interpreted from their original AUIPC/load/return bytes;
their results are not scripted call returns. Their backing bytes are explicit
synthetic inputs. Neither selected getter writes the counter. The known
bypass therefore preserves its entry counter through the selected lookup,
under the stated mapped-memory and noninterference conditions.

For index 0–3 the actual halfwords are `[150,180,65386,65356]`. Adding 2050
and retaining the low halfword produces `[2200,2230,1900,1870]`. This recovers
numeric behavior; it does not identify physical units or a product feature.

## Stops and case counts

| Stop before instruction | Cases per compiler profile | Meaning |
| --- | ---: | --- |
| `0xA110` | 1,600 | Before external registration call `0x9124` |
| `0xA1DE` | 800 | Before external cancellation call `0x90B0` |
| `0xA1E8` | 600 | Before frame restoration, from a gate/flag exit |
| `0xA168` | 420 | Before packet-field packing, numeric result ready |
| `0xA158`, window 1 | 180 | Analysis stop before reading outside selected DATA |

The last row is **verifier policy**, not an original check, return status,
trap or observed device fault. For example, a seeded counter of four reaches
the pre-read address `0x1AB50` without this invocation executing `0xA0FA`.
That proves the behavior of this chosen post-copy snapshot, not its physical
reachability or the contents of any larger table.

The model contains only the four selected halfwords as addressable Flash
DATA. No unselected table values are modeled, extracted or output. The full
BIN is still read to verify its SHA-256 and decode selected **code**; this is
not a claim that file I/O reads only eight bytes.

## Counter origins: what is established and what remains

`audit.py` checks the original reset zero-loop operands and finds GP+176
inside its configured word-clear range. If that loop completes with normal
accesses, the counter is zero at that point. It also checks the original
masked update sequences ending at `0xA0FA` and `0xA344`; enumeration of all
256 old bytes yields exactly four outputs, each occurring 64 times. A causal
interpreter test executes the first update path for all 256 old bytes.

These origins support the eight-byte lookup **conditionally**: a reset or
masked value in 0–3 must still be present when the bypass reads GP+176.
They do not prove that no earlier copy, other callee, alias, interrupt or DMA
write changed it. Starting after the copy deliberately leaves that provenance
boundary explicit. The other masked writer is not a dominator of this read.

The independent address audit enumerates all 256 possible byte indices.
Their halfword envelope is `0x1AB48..0x1AD48` (512 bytes), of which 328 bytes
lie beyond the supplied APP image. This is arithmetic on possible addresses,
not a table-size declaration, an actual read, or evidence of a firmware defect.
The separate geometry audit enumerates all 4,096 extracted 12-bit fields;
exactly the 179 values 1961–2139 pass. These audits are static calculations,
not full original-function execution for every combination.

## Corpus and mutation checks

The matrix combines cached/current status values 0/1/255, zero/nonzero flag,
five geometry boundary/interior values, five mode values and eight counter
values including 0–4, 91, 92 and 255. A fixed RAM pattern plus explicit writes
supplies the initial snapshots. This is finite evidence, not exhaustive state
coverage or proof of ordinary calling conventions.

The wrong compiled variants invent an index mask, increment the bypass index,
compare status truth rather than exact bytes, accept the next geometry value,
reuse cached status instead of the getter sample, change the table bias, or
wrap the counter only to a byte rather than mask to three. Each has a final
register/memory/PC/analysis-boundary mismatch. Logical trace differences alone
are insufficient for these checks; some numeric mutants have equal access
traces and are caught through register results.

## Reproduce offline

Use Windows x64, Python 3.10+, the existing pinned Clang/LLD 18.0.2 tools and
the archived decoded APP. From repository root:

```sh
python -B experiments/v4160-counter-bypass/verify.py --tool-dir /path/to/llvm/bin
python -O -B experiments/v4160-counter-bypass/verify.py --tool-dir /path/to/llvm/bin
python -B experiments/v4160-counter-bypass/test_oracle.py
python -O -B experiments/v4160-counter-bypass/test_oracle.py
```

The APP must have 76,800 bytes and SHA-256
`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.
Tool hashes are pinned, and source hashes are checked before/after execution
without claiming atomic filesystem snapshots. Generated host DLLs have no
CRT/DLL-entry dependency and are unloaded before temporary cleanup. The
worker has a 120-second timeout; individual builds have 30-second limits.

Distinct host arrays represent 65,536 bytes at `0x20000000` and eight bytes
at `0x1AB48`. Registers, call/event records and results have separate storage.
Numeric addresses resolve only into these arrays. No physical-address cast,
target function pointer, resident code or hardware operation is used. All
compared accesses are aligned and mapped. C uses volatile bytes and store
readback; abstract event widths do not establish bus width, atomicity, timing,
fault/trap equivalence or asynchronous effects. Intermediate registers are
compared at calls/stops rather than after every original instruction.

`source-provenance.json` records adapted helpers/decoder/build patterns and
the existing curated instruction/DATA sources. Earlier scripts are not runtime
dependencies. `verification.json` records both Python modes, compiled runs,
causal tests, decoded origins and mutation witnesses. The bounded decoder is
not a certified emulator.

The regular source build and 76,800-byte reproduction are unchanged and were
not rebuilt here. Global bounds for this and the other DATA aliases, the
preceding copy and scheduling contracts, complete normal-entry reachability
and installed resident/runtime identity remain unresolved. Analysis is offline;
GitHub publishes the results.
