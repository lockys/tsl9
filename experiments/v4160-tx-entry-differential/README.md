# TX entry: compiled C semantics with opaque return actions

This offline experiment reconstructs original TX entry `0x8A56` through
three boundaries, stopping **before** their next instruction:

| PC | Meaning |
| --- | --- |
| `0x8B6C` | Entry unsigned length guard rejected; before JR RA |
| `0x8ACA` | Frame restored after handle/provider rejection; before JR RA |
| `0x8ACE` | Bank selected; before bank preparation |

The model executes as a generated Windows host DLL compiled as C11/C++17
at `-O0`/`-O2`. A separate bounded RV32/RVC interpreter decodes the original
BIN and compares the same fixtures. No original target or resident code runs.

Each profile passes **1,610 cases**. Comparison includes both entire mapped
memory arrays, all 32 final registers, the boundary PC, call count, and the
ordered abstract memory trace. Every synthetic call also records its target,
continuation and all 32 registers immediately after setting the link register.
This directly checks second-call inputs even if later code overwrites them.
Normal and optimized Python receipts agree; nine causal oracle tests pass.

## What the original entry actually does

1. Compare the complete unsigned A3 to 1039. An oversized input changes A5
   but performs no frame write or provider call.
2. Save S0/S1/S2/S3/RA in a 32-byte frame. Read the zero-extended handle at
   GP+150 and compare it to the **complete 32-bit** A0; reject sentinel 65534.
   Save original A0/A3/A2/A1 in S2/S0/S1/S3.
3. If eligible, load the provider pointer from `0x4013C`, set A1=GP+128,
   and make the first indirect call. Exactly A0=1 on normal return selects
   bank 0; A2 becomes zero. Other results fall through to the second check.
4. Read the second handle at **current** GP+154 and compare it to **current**
   S2, again excluding 65534. If eligible, reload `0x4013C`, rebuild A0=S2
   and A1=current GP+128, and call again. A2/A3 retain the first call's
   values until the second call. After its normal return, A2 is set to one
   before testing the complete A0 against one.
5. A failed second check/result restores the frame using **current** SP.
   It does not normalize A0 to zero. A successful bank selection retains
   post-provider S0/S1/S3; the entry length guard is not repeated here.

These are live-state dependencies, not evidence that the installed provider
actually changes those registers. In particular, a synthetic accepted entry
can reach `0x8ACE` with S0=`0xFFFFFFFF`; the prior completion experiment's
bounded length domain does not cover that state. These packages have not
been composed into a universally equivalent full TX implementation.

## Corpus and discriminating checks

The 1,600-case matrix combines five entry lengths (0, 1039, 1040, 65536,
`0xFFFFFFFF`), five handle values, both first/second match settings and
four result values for each possible call. A handle wider than 16 bits
still cannot match a zero-extended halfword. Duplicate paths are intentional;
960 matrix cases reject at the unsigned guard.

Ten directed cases add live GP/S2 redirection, inherited second-call A2/A3,
provider slot replacement, full-width `0x10001` results, unchecked
post-provider length, SP relocation, second-handle writes, saved RA writes,
other register changes and frame/handle aliasing. Backing bytes have one
deterministic pattern; this is finite evidence, not exhaustive state coverage.

Five deliberately incorrect C models are separately compiled and executed:

- Reusing entry GP for the second handle produces a state/boundary mismatch.
- Truncating provider results to 16 bits produces a state/boundary mismatch.
- Resetting A2/A3 before the second call produces a state mismatch.
- Restoring through entry SP produces a state mismatch.
- Reusing the first provider pointer produces the wrong second call target:
  `0x12345678` instead of required `0x2468ACE0`. The harness rejects that
  target before applying the second scripted return and records diagnostic 4.

The last witness is an observed target mismatch, **not** a successful
second-return final-state comparison. None of the other four mutants is
rejected solely because an abstract trace differs.

## Explicit opaque-call and memory contract

There are at most two caller-supplied return actions. Each pins an even
target, a 32-bit A0 result, up to four aligned writes and optional register
changes other than X0/A0. The interpreter and C model clear bit zero of the
loaded JALR pointer and set RA to the original continuation before taking
the call snapshot. The action applies writes, the A0 result and other
register changes, then resumes at that fixed continuation. Unused actions
are not executed. This assumes a **normal return**, independently of any
scripted RA change. It does not implement a provider, prove a calling
convention, or model nonreturn, exceptions or asynchronous effects.

Two separate host arrays represent 65,536 bytes at `0x20000000` and 512
bytes at `0x40000`. They are synthetic mappings, not physical MCU RAM/ROM
claims. Register, action, event and result arrays have separate host storage.
Numeric addresses are resolved only into those arrays, with no physical
address cast or target function pointer execution. Inputs used for comparison
have aligned accesses wholly contained in one region; unmapped accesses fail.

Events describe grouped little-endian logical accesses and call snapshots.
The C implementation uses volatile bytes; it does not reproduce native bus
width, atomicity, IRQ/DMA observations or MCU exception behavior. Diagnostic
fault flags are harness outcomes. They do not establish equivalent invalid
input behavior across C and the interpreter or a general native API contract.
Intermediate register assignments between recorded calls/boundaries are not
compared instruction by instruction.

## Reproduce offline

Use Windows x64, Python 3.10+, the existing pinned Clang/LLD 18.0.2 binaries,
and the archived decoded V4.1.60 BIN. From repository root:

```sh
python -B experiments/v4160-tx-entry-differential/verify.py --tool-dir /path/to/llvm/bin
python -O -B experiments/v4160-tx-entry-differential/verify.py --tool-dir /path/to/llvm/bin
python -B experiments/v4160-tx-entry-differential/test_oracle.py
python -O -B experiments/v4160-tx-entry-differential/test_oracle.py
```

The driver requires the 76,800-byte BIN SHA-256
`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`
and pins compiler/linker hashes. The worker has a 120-second timeout and
individual build commands have 30-second limits. Only generated host DLLs
are loaded, without CRT or DLL-entry dependencies, and unloaded before
temporary files are removed. Source hashes are checked before/after host
execution; this does not claim an atomic filesystem snapshot.

`source-provenance.json` identifies the earlier instruction reconstruction
and adapted interpreter/build patterns. There is no runtime dependency on
their scripts. `verification.json` pins tested sources and unit tests.
The interpreter is a bounded instruction subset, not a certified emulator.

The regular firmware build and its existing 76,800-byte reproduction are
unchanged and were not rebuilt in this experiment. Installed provider binding,
real ABI, valid RAM/DATA ownership and lifetime, resident tail execution and
whole-entry-to-tail composition remain unresolved. Analysis is offline; only
publication of these results uses GitHub.
