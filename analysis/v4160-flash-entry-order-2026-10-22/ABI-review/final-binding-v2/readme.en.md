# Current final CLI and ABI binding v2

This binding uses actual `native-final-cli/{c,cpp}` artifacts after explicit producer freeze. CLI SHA is `0f96c209…7fa89`; final receipts are `94df38a3…c2d9e` / `feb63cb4…28a66d`. Core, profile and component ELF remain unchanged; ELF is still `aeccc19d…0339d`. [繁體中文](readme.zh-TW.md)

Fresh independent parsing of six objects, IR and linked component matches the immutable base ABI review after only two in-memory location-label normalizations.100 bytes/38 static instructions, normal returns, A0 alignment after the first control read/before its write, and five known interior loop roles pass; each language rejects12 machine-byte and3 IR counterexamples.

Base seal `73d1375e…1eb0c` and first supplemental seal `02dbc879…d7c8bb`, including all members, remain untouched. The earlier producer nondefault-firmware forwarding limitation was fixed and regression checked with alternate-location/wrong-reference tests. This v2 is current.

Run `python replay.py --check`; optional `--context-json` supplies `project_root`, `prior_build`, `firmware`, `source_dir`, `parser` and mode-indexed `build_roots`. Firmware is passed directly to the independent original SHA gate, not through the producer CLI.

Equal100-byte extent does not preserve original boundary `+8`, every scratch GPR prefix, fault/nonreturn/interrupt equivalence or whole-image integration. Offline static component evidence only: no RV32 execution, emulation, network, hardware or BIN creation; not flashable firmware.
