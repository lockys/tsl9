# Conditional mode 1/3 lookup DATA

[繁體中文](README.md) · [Formal src and original-coordinate integration](../tsl9-record-mode-row-integration/readme.en.md)

Two C constant arrays contain 16 bytes each from the official APP windows `[0x1A088,0x1A098)` and `[0x1A0A8,0x1A0B8)`. Actual C11/C++17 objects are identical, with no CODE, imports, relocations, or complete provider aliases. Every native DATA byte matches its original window.

This directory retains the frozen experiment before source curation: the parent had 162 source files, and its native partial component contained 69,412B CODE + 4,098B DATA. The rows have since entered formal `src/`; use the integration link above for current replay. The old experimental verifier pins the historical manifest, so current-manifest drift must not be described as a successful historical replay.

See [writer provenance](../tsl9-mode-state-writer-contract/readme.en.md) for conditions and unknowns. Local modes 1 through 5 are not a global domain. Backing two rows does not define the full provider or prove physical RAM/ROM/IRQ/OTA compatibility. No whole conservative DATA envelope or excluded payload was read, and no flashable BIN was generated.

[C/C++ definitions](mode_rows.v1.c) · [Pinned inputs](inputs-v1.json) · [Native experiment receipt](verification-v1.json)
