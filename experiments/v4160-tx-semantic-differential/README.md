# TX header/copy: compiled C semantic differential

The earlier abstract C slice is now **compiled and executed on the host**, then
compared with the original RV32 instructions over synthetic shared RAM.
Each of C11 `-O0`, C11 `-O2`, C++17 `-O0` and C++17 `-O2` passes
**1,248 cases**: 4,992 host C calls per Python mode, plus compiled mutation
witnesses. Normal and optimized Python runs agree. This improves the semantic
evidence for the slice; it is not an all-input equivalence proof.

Both sides start at `0x8ACE`, after bank selection and any unknown admission
provider effects, and stop **before** executing `0x8B14`. The copy-body branch
at `[0x8B52,0x8B6C)` is included. Admission, checksum-store/finish, tail calls,
interrupts and provider implementations are outside the comparison.

## Compared behavior

The complete 140,000-byte RAM array and ten output register projections
(`A0..A6`, `S0`, `S1`, `S3`) must agree after every case. Original-instruction
load/store counts and write extents are also checked. They are observations
of the interpreter, not a trace of host C bus operations.

The matrix covers two address mappings, both banks, lengths 0/1/2/3/4/15/31,
eleven source offsets around the destination/header, and four 32-bit command
values. Additional nonaliasing cases cover 255, 256, 1039, 1040, 1050, 1051,
1052 and 65535 in both banks. Eight initial-memory patterns vary the data.
These are finite sweeps, not the Cartesian product of all inputs or memory.
Whole-array comparison checks untouched bytes as well as the written region.

Header/source aliasing and forward-overlap propagation are preserved: reads
see prior writes in the same array, rather than an initial payload snapshot.
Zero length preserves the incoming `A6`; checksum arithmetic retains low-byte
truncation while the command register itself stays full-width.

Four actual C source mutants are compiled and run at `-O2`: shifted payload
source, incorrect checksum mask, wrong length-header offset and changed
zero-length `A6`. Each must disagree with the original-instruction oracle.
Six additional oracle tests cover the alias witness, zero length, row-boundary
threshold, invalid domains, instruction-budget exhaustion and unsupported
instruction rejection, under both Python modes.

## Candidate RAM-row extent

Let `B=0x2000B18C`, `bank` be 0 or 1, and `n` be the then-live length.
The slice's destination starts at `D=B+1062*bank+6`. Header stores fill
`D..D+4`; the forward loop then writes `n` bytes starting at `D+5`.
Within the stated normal, nonwrapping memory model, its write interval is:

`[B+1062*bank+6, B+1062*bank+11+n)`.

For `0 <= n <= 65535`, the low-16-bit loop comparison does not wrap before
the index reaches `n`. Thus the loop visits `0..n-1`. The range arithmetic
fits within a **candidate** 1,062-byte row exactly when `n <= 1051`.
At 1051 the slice ends at the row boundary; at 1052 it writes one byte into
the next candidate row, or one byte beyond the candidate 2,124-byte
reservation for bank 1. The 1039 case leaves twelve row bytes after this slice.
These statements concern the proposed layout, not a physical RAM allocation.

The checksum store is outside this stop and requires an additional byte.
The 1051 threshold must therefore **not** be used as a complete-TX bound.
The entry guard's earlier length check also does not prove a post-provider
length invariant. Cases beyond 1039, including 65535, are explicitly synthetic
post-provider states in a sufficiently large host array, not proven reachable
firmware states or demonstrated device memory errors.

## Reproduce offline

The host harness requires Windows x64, Python 3.10+, and the pinned existing
Clang/LLD 18.0.2 tool directory. From the repository root:

```sh
python -B experiments/v4160-tx-semantic-differential/verify.py --tool-dir /path/to/llvm/bin
python -O -B experiments/v4160-tx-semantic-differential/verify.py --tool-dir /path/to/llvm/bin
python -B experiments/v4160-tx-semantic-differential/test_oracle.py
python -O -B experiments/v4160-tx-semantic-differential/test_oracle.py
```

The driver checks the full original decoded BIN SHA-256 before interpretation:
`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.
It compiles host-only DLLs without CRT dependencies or a DLL entry routine,
loads only the generated model, and removes temporary outputs after unloading.
A separate worker process has a 120-second timeout; compiler/linker calls
also have timeouts. The model never directly dereferences an MCU address:
original addresses are represented as indices in one live, finite host array.

`model.c` derives from the earlier composed-RAM candidate. Only its opening
comment and C++ assertion spelling change; `source-provenance.json` records
the origin and hashes. The actual function body is retained. `wrapper.c`
exports its register projection. `oracle.py` is a new bounded RV32 subset
interpreter for these two windows; it is not a certified general ISA emulator.
Unsupported instructions, unmapped accesses and exhausted budgets fail.
`verification.json` retains the actual normal/optimized results and identities.

## Limits and firmware status

Assumptions include valid, nonwrapping address/index mapping; byte-sized
octets; bank 0/1; length at most 65535; a live shared array with every source
and destination access in bounds; normal execution and stable memory without
IRQ, DMA, faults or MMIO effects. The C model splits the original initial
halfword store into two volatile byte stores. This experiment compares final
RAM/registers, **not** store width, atomicity, intermediate observations or
asynchronous equivalence. Volatile does not provide synchronization.

This package neither modifies the regular firmware build nor replaces its
instruction-level TX. The complete 76,800-byte equality milestone remains
unchanged and was not rebuilt here. Physical RAM ownership, aliases outside
the synthetic array, lifetime, admission behavior and complete runtime
contracts remain unresolved. No firmware/provider/device is executed, and no
hardware, network or firmware-setting operation is part of the analysis.
