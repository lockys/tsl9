# State-reader reconstruction

This is the earlier source-only milestone. For current integration evidence see [state/callback integration](../state-callback-integration-2026-10-24/readme.en.md).

[繁體中文](README.md)

Added [C/C++ source](../../src/native/receive/state_leaf_reads.c): 27 event-reader roots and two actual helper callees, **472 bytes / 153 instructions**. Both C11 and C++17 pass complete static original-byte checks: 438 non-control bytes match directly; ten branch/call relocations restore every original byte through static original-address encoding. This is not execution or emulation evidence.

[Instruction evidence](leaf-evidence.json) · [Specification](../../experiments/tsl9-state-callbacks/spec-v1.json) · [Results and hashes](summary.json) · [Positive replay checker](../../experiments/tsl9-state-callbacks/verify-source-v1.py)

Preserved A976/A9BC/E058 conditional bit packing and original read widths, B082's calls to A968/8202 plus its 16-byte frame and RA restore, and GP-relative pointer returns at D190/D754. Field meanings and valid RAM ownership remain unknown.

The curated collection now has 96 C/H files and 69 code units. Including independent pointer data, 140 comparisons / 280 objects pass; all prior 136 code results and 817 artifact records remain identical. The manifest is an exact one-file/one-unit 95-to-96 extension. Frozen checkers were preserved; an old whole-manifest replay on the new manifest is not claimed.

The new readers are **not yet merged into the startup component**. The retained component remains byte-identical at 9836B code + 516B data, 698 relocations and 82 unresolved symbols. Full positive original-byte audits of state-access 336B, feature-callback 314B and state-events **v2** 1308B passed in both languages. Next integration must avoid duplicating the parent's 42B at 82A8–82D2, preserve both of its control references, and retain the complete 13C4E notification path rather than its entry alone.

Feature candidate: a read-only diagnostic view showing field provenance, raw values and confirmed/inferred status, with firmware SHA-256 distinguishing different images sharing an App-displayed version. This is a proposal, not an implemented feature; field meanings, mapping and safe-read conditions still need proof.

Physical MCU/ROM/RAM/IRQ, private ABI, final placement and OTA compatibility remain unproved. No target/model/ISA execution, network or hardware access, or BIN generation/flashing. Commit/push remains held for historical privacy findings. The full goal remains active.
