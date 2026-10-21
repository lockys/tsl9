# Final native receipts bound to independent ABI evidence

This binding freshly checks six actual objects, IR and component ELFs in `native-sealed-inputs/{c,cpp}` against the immutable parent ABI review. Only two in-memory location labels normalize; no sealed evidence is rewritten. Final receipt hashes are `350c0025…f4fa19` / `a66ba2e7…ed848`, component ELF `aeccc19d…0339d`. [繁體中文](readme.zh-TW.md)

Program is100 bytes/38 static instructions. Normal returns, A0 alignment after the first control read/before its write, and five known interior loop roles pass; each language rejects12 machine-byte and3 IR counterexamples. The parent documents the exact94/102-byte diagnostic history and original metadata. Equal size does not retain original boundary `+8`, scratch prefixes, full fault/nonreturn/interrupt equivalence or complete image integration.

Run `python replay.py --check`. Optional `--context-json` supplies `project_root`, `prior_build`, `firmware`, `source_dir`, `parser` and mode-indexed `build_roots`. This reviewer actually forwards its firmware path into the original SHA gate and does not call the producer replay route. The sealed producer's replay currently supports its default reference firmware path; its nondefault `--firmware` forwarding limitation is recorded and does not weaken this review.

Offline static component evidence only: no RV32 execution, emulation, network, hardware operation or BIN creation; not a complete flashable firmware.
