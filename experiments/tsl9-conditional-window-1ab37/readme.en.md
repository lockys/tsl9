# Conditional 13-byte read window

[繁體中文](README.md)

This source supplies 13 bytes at nominal `[0x1AB37,0x1AB44)`. The existing [read-domain analysis](../../analysis/v4160-data-addresses-2026-10-21/retained-read-domains/README.md) includes this window in the local `0x1A078 + 16*mode + column` read set. This does not establish physical reachability, the original data type, or global index bounds.

Run `python scripts/verify-window-1ab37.py --tool-dir <LLVM_BIN> --candidate <CANDIDATE_BIN> --out <NEW_OUTPUT_DIR>` to compile C/C++ sources, read only this permitted window and the baseline permitted sections, and create nonflashable original-coordinate diagnostic ELFs. The 41 sections total 73,551 candidate-matched bytes: the original 73,538 plus these 13. Six numerical address witnesses and zero `PT_LOAD` remain; this establishes no complete provider, full BIN or hardware compatibility.
