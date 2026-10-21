# Clock memory and normal-return register reconstruction

This C11/C++17 component adds source-specific register effects to the earlier
clock reconstruction. The original query writes only A2–A5; the field function
writes only A4/A5. A3 from the query survives the known
`9A42 → 1973C → 9F4C → 131C2` prefix and is presented to the unresolved
callback at `0x131E0`, fetched through `READ32(0x4004C)`. A conventional C
calling convention cannot justify discarding that value.

The shared C keeps all prior fresh MMIO, GP and table accesses. It additionally
reconstructs every query A3 branch residue, assigns A2 only on the external PLL
path, and commits the query's final A4/A5. The fields function retains A4=1000
and the full A5 product before halfword truncation. For example, 528,000,000
produces A5=66,000 while the stored halfword is 464.

## Offline host checks

```sh
sh experiments/tsl9-v4160-clock-registers/verify.sh --language both
```

Alternatively use `python3 -B experiments/tsl9-v4160-clock-registers/verify.py
--language both`. Python 3.10+ and a C11/C++17 compiler are required. `CC`/`CXX`
select single compiler executables; `PYTHON` selects Python for the shell entry.
The verifier downloads nothing. It reuses the unchanged prior memory fixtures,
checks their hashes, validates the sealed 214-byte / 69-instruction source with
50 raw controls, then checks the original integer destination fields against
the sealed register review. The layout resolver supports the investigation
and published `analysis/` layouts; it directly reuses the sealed decoder
without depending on the historical helper's old CLI directory prefix.

Each language has six groups / 293,845 host checks. The added checks observe
all query path residues, conditional A2 assignment order, live shifts and full
field outputs across the existing PLL, shift-byte and quotient-boundary cases.
`--tests-only` explicitly omits the source proofs. Receipts hash the actual
inputs, compiler and host executable. Only these synthetic host tests run.

## Native constraints and remaining work

The native branch uses compiler-specific empty physical-register barriers,
an explicit unsigned DIVU primitive, and separate reservation flags for each
function. Compile/link and ELF-bound register/CFG checks are documented under
`analysis/v4160-clock-abi-2026-10-21/compiler-review/`. A native compiler that
cannot meet those checks fails; the source does not silently add a stack
wrapper or allow extra registers.

The query candidate is 196 bytes versus its original 174-byte extent, so it
cannot replace that body at the original placement. The field candidate is
38 bytes versus the original 40 bytes. These sizes do not establish image,
caller, interrupt, ROM or hardware compatibility. Query native branch semantics
are not completely proved by structural checks and host tests. Empty barriers
do not establish asynchronous timing or intermediate register equivalence.
No original entry is replaced, no RV32 is executed or emulated, no peripheral
is accessed and no BIN is generated. The final flashable-image goal is open.
