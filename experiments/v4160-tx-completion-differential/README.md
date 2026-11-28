# TX completion: checksum, restores, metadata and pre-tail state

The compiled C semantic model now covers the original **post-selection path
from `0x8ACE` to the stop before `0x8B50 JR T1`**, including header/copy,
checksum storage, stack restores, metadata writes and fresh tail/selector
reads. It does not execute admission, the indirect tail transfer or any
provider. The original frame/register ABI is represented as data, not used
as a callable host ABI.

Each of C11 `-O0`, C11 `-O2`, C++17 `-O0` and C++17 `-O2` passes
**1,940 cases**. Every case compares all three mapped memory regions,
**all 32 registers**, and the entire ordered abstract memory-access trace.
Normal and optimized Python results agree. This is finite differential
evidence, not a universal equivalence or physical-memory proof.

## Why the order matters

After the payload loop, the original accesses occur in this order:

1. Store checksum at `B+1062*bank+11+length`.
2. Read saved RA, S1, S2 and S3 from SP+28/+20/+16/+12.
3. Store `u16(length+6)` at bank base+2, then zero at bank base+4.
4. Read saved S0 at SP+24.
5. Read T1 from the word at `0x40050`.
6. Read A0 from byte `GP+148+4*bank` and advance SP by 32.

The fixtures include checksum aliasing saved RA, metadata aliasing saved S0,
metadata aliasing the selector, and saved S0/selector aliasing the tail word.
The alias layouts are not mutually exclusive. In particular, values restored
before metadata need not equal the final memory word after metadata writes.
The model therefore does not snapshot stack words or selector values early.

Four deliberately incorrect C models are actually compiled and executed:
wrong checksum offset, wrong metadata length, RA prefetched before checksum,
and S0 prefetched before metadata. All have a concrete **memory or register
state mismatch**, not merely a differently ordered trace. The receipts record
the first witness. Eight separate oracle tests retain causal alias examples,
the exact finish-access order, metadata wrap and bounded failure cases.

## Data and boundary observations

`B=0x2000B18C`, the candidate bank stride is 1062, and header start is
`B+1062*bank+6`. With checksum included, header/payload/checksum occupies
the relative interval `[6,12+length)`. Metadata also writes `[2,6)`.
For the stated normal, nonwrapping model, all destination writes therefore
occupy `[2,12+length)` within the selected candidate bank.

This interval fits the candidate 1,062-byte bank when `length <= 1050`.
At 1051, the checksum reaches one byte into the next candidate bank, or
beyond the candidate two-bank reservation for bank 1. This updates the
previous header/copy-only threshold of 1051, which excluded checksum.
It does not establish physical allocation, a reachable state or a device fault.

The corpus includes 1039/1040 and 1050/1051/1052, plus metadata wrap cases:
length 65529 emits metadata 65535, 65530 emits 0, and 65535 emits 5.
The values are the original low-halfword behavior; no clamp is added.
Lengths beyond the earlier entry guard are synthetic **post-provider** values,
not proof that the original entry/callee sequence produces them.

At the stop A1 is 1; A2 is the selector address; A3 is B; A4 is checksum;
A5 is `0x40000`; A6 retains the copy-loop result. RA/S1/S2/S3 were restored
before metadata, S0 afterward, and T1 is the fresh tail word. Other registers
are also compared, including unchanged GP. `T1 & ~1` would be the encoded
next transfer address, but it is never converted to a host function pointer
or executed here.

## Harness and memory abstraction

The model uses explicit little-endian byte operations over three disjoint
address mappings: 140,000-byte synthetic RAM, 512 bytes at `0x20004000`, and
128 bytes at `0x40000`. Each has a separate live host byte array. This permits
word/halfword/byte aliasing in a mapping without incompatible typed C objects
or integer-to-host-pointer casts. Register and trace storage are separate.
Those mappings do not claim that equivalent physical MCU memory exists.
Compared fixtures require aligned halfword/word accesses, with each complete
access contained within one mapping. The oracle checks these conditions;
the C byte resolver alone does not enforce them.

Each abstract access records kind, address, width and value. A C grouped
word read still comprises four volatile byte reads; a grouped halfword store
comprises two byte writes. The event widths label the abstract operation,
**not** generated host bus transactions, atomicity, faults or IRQ/DMA-visible
intermediate states. Equating the event streams does not prove those effects.
The harness rejects any mapping/trace-capacity fault in the valid corpus;
its fault flag is not an emulation of MCU exception behavior.

The matrix combines both banks, two RAM address mappings, six short lengths,
five source/header offsets, four stack layouts and four selector layouts.
Commands sample four 32-bit values and are correlated with selector choice,
rather than forming an independent command-by-selector sweep. Twenty additional nonaliasing large
length cases complete the 1,940 cases. This is not all combinations of every
input, memory content or program state. Some internal synthetic stacks are
word-aligned without satisfying a standard public C ABI's stack alignment.

## Reproduce offline

Requirements: Windows x64, Python 3.10+, the pinned existing Clang/LLD
18.0.2 tools, and the archived V4.1.60 decoded BIN. From repo root:

```sh
python -B experiments/v4160-tx-completion-differential/verify.py --tool-dir /path/to/llvm/bin
python -O -B experiments/v4160-tx-completion-differential/verify.py --tool-dir /path/to/llvm/bin
python -B experiments/v4160-tx-completion-differential/test_oracle.py
python -O -B experiments/v4160-tx-completion-differential/test_oracle.py
```

Before interpretation, the driver requires the 76,800-byte original SHA-256
`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.
Only generated host DLLs are loaded, without CRT or DLL-entry dependencies;
temporary files are removed after unloading. The worker has a 120-second
timeout, and compiler/linker calls have separate timeouts. Missing or changed
required inputs fail rather than skipping work. Source hashes are checked
before and after the run, without claiming atomic filesystem snapshots.

`model.c` reimplements and composes the prior header/copy and independent
finish contracts in the mapped-byte abstraction. `oracle.py` extends the
earlier bounded RV32 interpreter with the original completion loads, shifts
and stack operations. It is not a certified general ISA emulator.
`source-provenance.json` identifies those reference inputs;
`verification.json` records the actual host runs and mutation witnesses.

The regular firmware source and 76,800-byte equality milestone are unchanged
and were not rebuilt here. Admission/provider behavior, valid installed RAM,
global DATA bounds, lifetime/exclusivity, private ABI and actual resident/tail
execution remain unresolved. No target firmware or hardware is run, and the
analysis uses no network or firmware-setting operation.
