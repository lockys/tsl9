# TX entry-to-pre-tail composition: compiled C versus continuous original ISA

The previously separate entry and completion C models now run with **one
memory object, one register array and one ordered event stream**. Provider
actions and entry frame writes remain visible to bank/header preparation,
forward payload copying, checksum, metadata, stack restoration and tail reads.
The original-instruction oracle starts at `0x8A56` and uses one decoder loop
across `0x8ACE`; it does not restart a second interpreter at that boundary.

The experiment compares generated host C11/C++17 at `-O0`/`-O2` against the
original decoded BIN. Each profile passes **2,587 cases**, split as follows:

| Stop before instruction | Cases per profile | Meaning |
| --- | ---: | --- |
| `0x8B50 JR T1` | 1,069 | Accepted, completed through fresh tail/selector reads |
| `0x8ACA JR RA` | 557 | Entry/provider rejection after frame restoration |
| `0x8B6C JR RA` | 960 | Oversized entry rejected before frame creation |
| `0x8ACE`, diagnostic domain 6 | 1 | Explicit harness stop before bank preparation |

Thus **2,586** cases reach a rejection or pre-tail instruction boundary; one
is a separately identified model-domain stop. All three JR instructions remain
unexecuted. No resident function, device or physical firmware execution occurs.
Normal and optimized Python results agree; ten causal oracle tests pass.

## Composition evidence

For each case, the harness compares both entire mapped memory arrays, all
32 final registers, final PC, call count, domain diagnostic and the complete
ordered abstract event stream. Each synthetic call records target,
continuation and all 32 registers immediately after setting its link.
The composition boundary `0x8ACE` also records all 32 registers. Recording
this checkpoint does not restore registers, discard writes or reset events.

The C completion stage uses post-provider S0/S1/S3 as length/source/command,
current GP for the final selector, and current SP for restoration. It does not
replace them with original arguments or reapply the entry's 1039 limit.
The directed `composed_live_state` fixture changes all five dependencies and
writes payload, saved RA, selector and tail backing bytes. Its final state
includes RA=`0xDEADBEEF`, SP=`0x2000D060`, GP=`0x20004100`, raw
T1=`0x87654321`, A0=`0x5A` and checksum=`0x87`.

Additional causal tests check:

- A first provider's payload write survives a failed first result and is
  copied after a second provider accepts bank 1; second-call A2/A3 retain
  the first call's changes.
- A forward overlapping source observes preceding copy writes rather than
  a source snapshot. A four-byte example produces four bytes of value four.
- Checksum aliases saved RA, and metadata aliases saved S0. RA is read after
  checksum but before metadata; S0 is read after metadata. Restored values
  can differ from the final contents of their earlier backing words.
- The saved S0 word, tail word and selector can share backing bytes. Raw T1
  retains its low bit at the stop; no host target is called.
- Lengths 65529/65530/65535 traverse entry plus a scripted normal return and
  emit metadata 65535/0/5 respectively. This is synthetic reachability only.

Six deliberately incorrect C models are separately compiled and executed:
reuse entry length, source, command, GP or SP at composition, and write
checksum at the wrong offset. Each has a final memory/register/boundary
mismatch. A mere difference in logical access order is insufficient to reject
these mutants. `verification.json` records the actual first witnesses.

## Corpus and finite scope

The corpus contains the earlier 1,600 entry combinations and ten directed
entry cases, one combined live-state fixture, 960 accepted alias fixtures,
and 16 longer post-provider length cases. The alias matrix combines both
banks, five short lengths, six source offsets, four final frame locations and
four final selector locations. Frame and selector changes in that matrix are
injected by an accepted opaque return, after the original entry saves.

The 16 long cases use both banks at lengths 1039, 1040, 1050, 1051, 1052,
65529, 65530 and 65535. Source bytes come from a disjoint synthetic region;
destination copying can overwrite the entry frame before it is restored.
The earlier conditional 1,062-byte candidate-bank boundary still fits the
header/payload/checksum destination interval only through length 1050.
These larger mappings and cases do not prove installed allocation or faults.

Backing memory uses one deterministic pattern plus explicit writes. This is
finite differential evidence, not exhaustive state exploration, universal
equivalence, a complete native ABI, or instruction-by-instruction comparison
of every intermediate register assignment.

## Explicit domain stop

The original loop compares `uint16(counter)` with the complete unsigned S0,
while source/destination indexing uses the full counter. If S0 exceeds 65535,
that comparison cannot select the normal loop exit. Unmapped accesses,
asynchronous state changes and device behavior are separate questions.

Both harness implementations therefore stop at `0x8ACE` before bank
preparation when post-provider S0 exceeds 65535. They retain the preceding
entry/provider state and report **domain 6**. The corpus has one such case,
with S0=`0xFFFFFFFF`; a causal test separately checks the exact 65536 boundary.
Domain 6 is a verifier policy, not an original instruction, exception, status
code, observed infinite loop or completed TX path. Lengths within the domain
can still fail mapping/alignment checks and are not automatically valid inputs.

## Opaque return and memory assumptions

Up to two actions describe a chosen provider target, A0 result, up to four
aligned writes and optional other register changes. The loaded call pointer's
low bit is cleared; RA is set to the original continuation. After recording
the call snapshot, the action applies writes, its result and register changes,
then resumes at that fixed continuation. This assumes a normal return even
if the action changes RA; it does not execute or characterize resident code.
Unused actions do not run. No real provider binding, preservation guarantee,
nonreturn behavior or hardware reachability is inferred.

Two disjoint host arrays represent 196,608 bytes at `0x20000000` and 512 bytes
at `0x40000`. This unifies the previously separate synthetic RAM/GP backing
and provides space for long sources/destinations. The arrays do not assert
equivalent physical MCU memory. Registers, actions, events and result storage
are separate host objects. Numeric addresses are resolved into these arrays;
no physical-address cast or target function-pointer conversion occurs.

Valid compared accesses are aligned and contained in one mapping. Events
describe grouped little-endian logical accesses; calls and checkpoints are
additional harness records. C implements accesses with volatile bytes,
including store readback. Event widths do not establish native bus widths,
atomicity, timing, IRQ/DMA-visible intermediate behavior or trap equivalence.
The C fault flag and Python exceptions are diagnostics with different invalid
input semantics. Such failures are not successful comparisons.

## Reproduce offline

Use Windows x64, Python 3.10+, the existing pinned Clang/LLD 18.0.2 tools and
the archived decoded V4.1.60 BIN. From repository root:

```sh
python -B experiments/v4160-tx-integrated-differential/verify.py --tool-dir /path/to/llvm/bin
python -O -B experiments/v4160-tx-integrated-differential/verify.py --tool-dir /path/to/llvm/bin
python -B experiments/v4160-tx-integrated-differential/test_oracle.py
python -O -B experiments/v4160-tx-integrated-differential/test_oracle.py
```

The 76,800-byte image must have SHA-256
`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.
Tool hashes are pinned. The host worker has a 120-second timeout; each build
command has a 30-second limit. Generated DLLs have no CRT/DLL-entry dependency
and are unloaded before temporary files are removed. Sources are hashed
before and after execution, without claiming an atomic filesystem snapshot.

`source-provenance.json` records the adapted entry/completion sources.
This package has no runtime dependency on their scripts. The unified oracle
is an independently structured decoder relative to the abstract C model,
but it remains an adapted, bounded ISA subset rather than a certified emulator.

The regular firmware source/build and existing 76,800-byte reproduction are
unchanged and were not rebuilt here. Installed provider bindings, actual
resident/tail execution, valid RAM/DATA ownership and lifetime, private ABI
and whole-firmware integration remain unresolved. Analysis is offline;
publication of these results uses GitHub.
