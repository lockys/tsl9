# UUID registered in the source-only build

The GATT UUID source is now registered in both source manifests and included in
the regular selected-span build. The manifests list **174 C/C++ source/header
files, 125 CODE units and 14 DATA units**. The previous UUID experiment's
separate frozen-parent diagnostic remains historical evidence.

At `[0x1AB44,0x1AB46)`, the named `tsl9_gatt_write_UUID_1ab44` OBJECT now owns
`F1 FF`. The old four-byte opaque object was removed. Only its remaining
two zero bytes at `[0x1AB46,0x1AB48)` stay opaque. Those zeros have no new
semantic or padding interpretation. The upstream relative jump-table
reconstruction and its symbol-ownership guard are retained.

This migrates two bytes of ownership; it adds **zero** selected bytes. The
source-only build still selects **73,672 bytes**, now in 6,268 nonoverlapping
sections. Both languages have 141 freshly compiled registered units, including
the window/opaque units. TX is independently compiled and replaces the old
transport input as in the existing pipeline. No historical object or candidate
BIN is used as a build input. Native input-object bytes are rebuilt rather than
borrowed from the previous 73,538-byte formal layout.

## Actual verification

Normal and optimized Python builds/checks agree. The optimized build used
`PYTHONOPTIMIZE=1` so optimization also applies to Python subprocesses.
Both C11/C++17 selected payloads retain SHA-256
`ef9d3be753f02d5802a2c2feda99aa94b9b3c3acc2b55d32f8f480719d658a54`.
Every selected byte is compared with the original decoded BIN: the inherited
**93 differing bytes remain wholly within TX `[0x8A56,0x8B6E)`**. The UUID
matches its original coordinates. The selected digest does not establish
complete firmware equivalence.

The checker verifies complete manifest provenance, fresh unit inventories,
unique UUID/tail sections and OBJECT symbols, unchanged relative-table owners,
equal C/C++ bytes, exact inherited dependencies, entry zero and no `PT_LOAD`.
Ten ownership/header tests run against each language under both Python modes;
they reject missing/duplicate/obsolete owners, overlap, wrong symbol size or
section, byte corruption, nonzero entry and a loadable program header.

Eight source-aggregate dependencies remain before the inherited numerical stack
witness; the later strict diagnostic link still fails on seven dependencies.
Those differ from the six UND symbols in the older frozen formal parent:
the fresh source-only pipeline also exposes the stack and candidate TX RAM
requirements. No provider is resolved by this UUID migration. Numerical
witnesses remain diagnostic conveniences, not installed ROM/RAM evidence.

## Reproduce offline

Use the existing LLVM directory and Python 3.10+ from the repository root:

```sh
python -B scripts/verify-curated-source.py
python -B scripts/build-source-spans.py --tool-dir /path/to/llvm/bin --out /new/external/output
python -B experiments/v4160-gatt-uuid-integrated/check.py --build-root /new/external/output --original /path/to/ID-2966-V4.1.60-decoded.bin
python -B experiments/v4160-gatt-uuid-integrated/test_ownership.py --build-root /new/external/output
```

Build output must be a new directory outside the repository. Repeat using
`python -O -B`, with `PYTHONOPTIMIZE=1` in the environment, and a different
new output directory. No network or hardware is needed. The original is read
only and must match the fixed image SHA-256 checked in `check.py`.
Builds compile the registered source tree and compiler headers; only the audit
reads the original BIN. The two excluded ranges are omitted from selected
payloads. This is a nonloadable diagnostic, not a complete or flashable BIN.

`verification.json` records both actual audits; `source-change.json` records the
published parent and its pinned inputs. The old 95.75% formal proof was not
reissued here and its receipts must not be relabeled as this fresh build.
Installed ROM, private ABI, RAM ownership, startup/IRQ, provider contracts and
device/OTA behavior remain unproved. Next useful provider work is the observed
four-byte defaults literal at `0x1A69C`, while retaining the three conditional
DATA providers and unknown resident entry as unresolved.
