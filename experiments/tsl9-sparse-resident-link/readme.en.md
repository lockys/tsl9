# Sparse resident reference link

This check places a hash-pinned WCH V1.31 reference into **17 separate sections**, preserving original addresses and gaps. The `0x40000` entry is section-backed. Under the existing data-alias and RAM assumptions, the C and C++ `--no-undefined` links complete and APP sections match the candidate image; the diagnostic ELF has no `PT_LOAD`.

This only establishes how the linker handles the symbols currently referenced: each ELF still has 44 undefined symbol-table entries, so it does not close all dependencies. The candidate startup's second copy reads `[0x6EAA4,0x6EB30)`, but the reference ends at `0x6EB2C`, **missing the final 4 bytes**; no gaps are filled. The WCH reference does not establish that the device has the same resident, correct RAM/ABI or flashability.

First run `scripts/build-v4160-source-candidate.py` with a new output directory outside the project, then run:

```sh
python scripts/verify-sparse-resident-link.py --project-root . --conditional-dir <BUILD_DIR>/conditional-link --reference-dir <WCH_REFERENCE_DIR> --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>
```

The existing pinned reference and `source-map.json` are required. The existing 17 sections already include the separate 136-byte tail. Before linking, the check now validates the [pinned original HEX](../../analysis/v131-startup-source/README.md), compares every segment byte and its complete coverage against it, and preserves the final four unrecorded bytes as a hole. Run `python -B tests/test_sparse_resident_evidence.py` for real-input and contamination/forged-map controls. No download or hardware access occurs; outputs are offline diagnostics and are not device-validated. The no-provider strict link must still fail; diagnostic reference linking does not change the product strict gate or prove completeness.

A [follow-up symbol audit](../tsl9-diagnostic-discarded-symbols/readme.en.md) classifies the 44 entries as 43 alternative definitions in discarded sections and one originally undefined symbol; the 24 input relocations to them all originate in discarded sections.

**Linker controls:** Without a resident provider, both C and C++ strict links fail on `tsl9_boot_resident_40000`; with only the reference entry's first 4 bytes, both links still succeed. Those four-byte control ELFs have no `PT_LOAD` or other reference sections. This demonstrates that successful linking alone cannot establish resident completeness or boot behavior.
