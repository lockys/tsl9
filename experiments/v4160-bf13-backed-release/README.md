# BF13 section-backed witness

This offline static witness compiles the six SHA-256-pinned input snapshots as
C11 and C++17, extracts the RAM carrier with relocatable GC, and links the two
leaf functions with the section-backed alias. The final 10-byte sections are
checked against the pinned firmware bytes. The carrier, alias, globals,
relocations and allocated sections are checked as well. The bounded ELF reader,
compiler, linker and used resource header are pinned; include paths are
restricted and traced. Commands have an allowlisted environment and closed
stdin.

The linker script discards `.riscv.attributes` to avoid LLD's extra RISC-V
attributes program header. The final ELF must have **exactly one program
header, of type PT_NULL**; PT_LOAD, PT_INTERP, PT_DYNAMIC and missing/extra
headers are rejected by raw-byte mutation tests. PT_NULL's other fields are not
pinned. Each language checks the complete set of 68 negative IDs and exact
reasons. The reader only accepts the known section-type whitelist; RELR and
unknown types fail instead of being silently treated as no relocations. It also
checks the all-zero symbol 0, the `sh_info` local/global boundary and binding
partition, and SECTION symbol metadata before the witness excludes SECTION
symbols from its member comparison.

Raw mutations cover the actual full, GC and final ELFs for RELR, unknown
section type, each symbol-0 field, boundary and binding errors. The pinned LLD
emits SECTION symbols only in the GC carrier; its actual SECTION records are
mutated for name, value, size, binding, other and section index. The binding
case is checked both at the partition and in a global slot, isolating the
metadata check. All mutations require their specific rejection reason.

`probe.py` is approximately 17.9 KB, not strictly under 10 KB. This is a size
constraint, not a technical failure; guards were retained for safety. No
under-10-KB compliance is claimed.

Reproduce on the pinned Windows NDK host:

```powershell
$py = 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe'
& $py -I -B experiments/v4160-bf13-backed-release/probe.py
& $py -I -B -O experiments/v4160-bf13-backed-release/probe.py
& $py -I -B experiments/v4160-bf13-backed-release/test_probe.py
& $py -I -B -O experiments/v4160-bf13-backed-release/test_probe.py
```

The CLI accepts no arguments and only optimization levels 0 or 1 with `-I -B`;
`-OO` is rejected. The test runs the complete `probe.py` source from verified
bytes (SHA-256 `c5c8c18a296d858cb1fc7891fa0c6171ba563b1d7ca1b4599bfec86cb99342f9`)
in both modes, verifies the exact negative ID/reason map and leaf bytes, and simulates
missing and changed reads for each of the six inputs. These negative runs must
fail with empty stdout. It also checks invalid CLI modes.

This is a static address-model reconstruction, not proof of the original
source owner, complete original unit, calling ABI, physical RAM or execution.
The reader is not a general untrusted-ELF validator, and the witness does not
claim the upstream full reset/leaf relocation checks. No target is executed.
Pins do not eliminate local TOCTOU; Python, OS, compiler dependencies and DLLs
are not comprehensively pinned. Assume no concurrent replacement during a run.
