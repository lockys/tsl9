# V4.1.60 counter lookup: bounded instruction check

The pinned original RV32 instructions now agree with the derived address formula
over **138,240 synthetic cases**. Starting at `0xA0E2`, after the unknown indirect
provider has returned, the equal/nonzero branch skips the counter update. With
counter 4, stack field 1961, and selector 0, the load at `0xA158` addresses
`0x1AB50` with width 2, beyond the selected eight-byte window
`[0x1AB48,0x1AB50)`. The checker stops before reading the table value.

This closes the instruction-interpretation gap in the earlier
`v4160-counter-bypass-composition-next` abstraction. It does **not** prove
reachability of counter 4, actual provider behavior, complete table size,
device behavior, or a product bypass. The selected eight-byte window is not
an established memory allocation boundary.

## Reproduce offline

Python 3.10+ standard library only; from this directory:

```sh
python -B verify.py
python -O -B verify.py
python -B -m unittest -v test_verify
python -O -B -m unittest -v test_verify
```

Supply the existing decoded BIN at the repository-relative path in `verify.py`.
It is read only, must be 76,800 bytes, and must match SHA-256
`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.
No firmware is included here. `result.json` retains the actual verification
receipt. Hash identity does not establish external authenticity.

The decoder was written for this experiment using the RV32 instruction fields;
the selected instruction windows and formulas also have the earlier local
abstraction as a reference. Local radare2 6.2.4 RV32 disassembly was used to
cross-check both leaf addresses, branches, and the load. This is not an
independently certified ISA emulator. The tests include in-memory shift,
branch, and load mutations, image identity rejection, unmapped reads, unexpected
control, budget exhaustion, register wrapping, both zero edges, and range bounds.
Mutated images are never saved or executed on a device.

## Coverage and assumptions

The matrix covers every counter byte against every selector byte, six input
boundaries through both zero-edge outcomes, the complete 4,096-value reconstructed
stack field domain, and all 65,536 aa/leaf combinations. These are separate
dimensions, **not** their complete Cartesian product. On the unequal edge it
stops at `0xA0EE`; it makes no prediction about later execution on that path.
The equal edge retains the counter; all 256 counter values remain representable
in the synthetic input. Values 0..3 yield addresses within the selected window;
4..255 yield addresses beyond it under the selected path conditions.

Memory and registers are explicit synthetic post-provider inputs, not observed
runtime state. Assumptions include normal completion of loads/calls, stable
nonaliasing memory, little-endian accessible stack and GP, and no IRQ, DMA,
faults, MMIO side effects, or concurrency. Both tiny byte-reading leaves execute
their original instructions; the unknown provider at slot `0x4004C` is outside
the slice and is never simulated.

No new C/C++ byte-identical region or loadable BIN is claimed. The previously
recorded formal reconstruction coverage stays **73,538/76,800 bytes (95.75%)**;
that aggregate was not re-audited by this experiment. Next work is to establish
counter writer provenance and the actual provider contract before drawing any
runtime conclusion.
