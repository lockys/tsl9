# Dispatcher table-bit checkpoint

`src/native/receive/ota_dispatch_142fc.inc` reconstructs the 50-byte continuation at `[0x142fc, 0x1432e)`. It depends on the original dispatcher frame and unconfirmed table and function contracts; it is not independently callable.

On the `origin/main` base, `compile_dispatch5` in `scripts/source-ota-epilogue.py` compiled and linked both C and C++ with Android NDK 27.1 LLVM at the original address. Object section, symbol and relocation checks passed, and both linked sections matched the corresponding 50 bytes of `src/native/tx_candidate/full-image-payload.json`. This carrier comparison is not independent evidence of behavior.

This is a staged checkpoint: the candidate builder, conditional-link verifier, isolation test and manifests still use the opaque carrier for this range. They must be integrated and verified together before claiming source replacement. Installed ROM, RAM ownership, runtime behavior and flash safety remain unproved; do not flash based on this checkpoint.
