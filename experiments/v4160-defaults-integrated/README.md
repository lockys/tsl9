# Defaults provider integrated in regular builds

The four observed bytes at `[0x1A69C,0x1A6A0)` now come from registered
`src/native/receive/defaults_read_window.c`. Both manifests list **175 C/C++
source/header files, 125 CODE units and 15 DATA units**. The original consumer's
`tsl9_settings_default_data_1a69c` reference binds to a real four-byte readonly
OBJECT; the regular diagnostic links no longer supply a numerical defaults
witness. These are opaque observed `31 32 33 34` bytes, without a NUL or a
recovered product meaning. Actual copy-provider effects remain unknown.

The regular source-only selection grows from 73,672 to **73,676 bytes** in
**6,269 nonoverlapping sections**. Its two spans are `[0x8000,0x14056)` and
`[0x14C8A,0x1AC00)`; the dispatcher code's 3,124 bytes remain outside this
selected-span profile. Both languages rebuild all 142 registered input units,
with the existing separately compiled TX replacement. No historical object or
candidate BIN supplies build bytes.

## Complete diagnostic assembly

The full candidate builder now inserts only dispatcher code between those two
spans. Defaults are included once, through the registered source aggregate.
The full conditional link also generates only the code provider and verifies
that defaults retain their real readonly section, address, size and bytes.
Its negative controls reject missing dispatcher code and an explicitly
discarded defaults section while preserving their actual consumers.

The existing dispatcher helper now travels with all 85 required `.inc` sources;
76 were already present locally but absent from the published parent. They
are included for reproducibility, not claimed as newly recovered code in this
milestone. Each fragment is compiled and checked at its original address
against the existing reference carrier, then reassembled into the diagnostic
code section. The fragment objects are **not directly linked** to the final
ELF, and the carrier comparison is not an independent source-origin proof.

Fresh C11/C++17 candidates are identical at **76,800 bytes**, SHA-256
`28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`.
Comparison against the original decoded image retains exactly the inherited
**93 different TX bytes** in `[0x8A56,0x8B6E)`. This is a diagnostic candidate,
not original-byte equivalence or verified usable firmware. No device is run
and no flashing is performed.

Dependency counts describe different link stages:

| Stage | Remaining dependencies |
| --- | ---: |
| Regular source aggregate | 7, including stack and candidate TX RAM |
| Original-coordinate strict link, with inherited numerical stack witness | 6 |
| Conditional TX RAM object | 5 |
| Three conditional DATA aliases and TX RAM | 2 |
| Conditional full dispatcher/code provider | 1: installed resident at `0x40000` |

The last stage's three DATA aliases, proposed RAM ownership and installed ROM
are still unproved. Giving the resident address numerically only permits a
nonloadable diagnostic with entry zero and no `PT_LOAD`. It does not complete
the remaining runtime contracts. The older formal **95.75%** proof is not
reissued or relabeled by this milestone.

## Offline reproduction and receipts

Python 3.10+ and a local RISC-V LLVM toolchain are required. From repo root:

```sh
python -B scripts/verify-curated-source.py
python -B scripts/build-source-spans.py --tool-dir /path/to/llvm/bin --out /new/external/selected
python -B scripts/build-v4160-source-candidate.py --tool-dir /path/to/llvm/bin --out /new/external/candidate
python -B experiments/v4160-defaults-integrated/check.py --build-root /new/external/selected --candidate-root /new/external/candidate --original /path/to/ID-2966-V4.1.60-decoded.bin
python -B experiments/v4160-defaults-integrated/test_ownership.py --build-root /new/external/selected
```

Output paths must be new directories outside the repo. The build uses source
and fixed local reference carriers; the separate checker reads the original
decoded BIN read-only and checks its SHA-256. Source-only builds and checks
also passed under `python -O -B`; `PYTHONOPTIMIZE=1` propagated that mode to
their subprocesses. The complete candidate was freshly built in normal mode,
then inspected under both Python modes; an optimized full candidate rebuild
is not claimed.

Sixteen ownership/header tests pass against both language ELFs in both Python
modes, including missing/duplicate/ABS defaults symbols, wrong size/bytes,
writable storage, overlap, prior UUID ownership, nonzero entry and `PT_LOAD`.
The regular conditional DATA-provider entry point is checked separately.

`verification.json` records the actual source audits and full candidate
inspection. Nested build directories retain compiler outputs and the
conditional/candidate `verification.json` receipts. `source-change.json`
records the pre-change local inputs; `spec.json` records the new DATA profile.
Earlier isolated defaults and UUID receipts remain historical profiles rather
than current manifest receipts. Installed ROM, private ABI, RAM, startup/IRQ,
copy behavior and hardware/OTA operation remain work to complete.
