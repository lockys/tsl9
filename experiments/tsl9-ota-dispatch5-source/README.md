# Dispatcher table-bit checkpoint

`src/native/receive/ota_dispatch_142fc.inc` reconstructs the 50-byte continuation at `[0x142fc, 0x1432e)`. It depends on the original dispatcher frame and unconfirmed table and function contracts; it is not independently callable.

On the `origin/main` base, `compile_dispatch5` in `scripts/source-ota-epilogue.py` compiled and linked both C and C++ with Android NDK 27.1 LLVM at the original address. Object section, symbol and relocation checks passed, and both linked sections matched the corresponding 50 bytes of `src/native/tx_candidate/full-image-payload.json`. This carrier comparison is not independent evidence of behavior.

The candidate builder and conditional-link verifier now compile and compare this fragment in both modes before replacing its carrier bytes. The 200-file isolated build passed, including the conditional-link failure control; both 76,800-byte outputs have SHA-256 `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`. Of the 3,128-byte carrier, 598 bytes are compiled from source and 2,530 remain opaque. Installed ROM, RAM ownership, runtime behavior and flash safety remain unproved; do not flash these outputs.
