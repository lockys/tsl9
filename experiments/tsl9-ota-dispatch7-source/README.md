# Dispatcher table gate and command filter

`src/native/receive/ota_dispatch_14370.inc` reconstructs 52 bytes at `[0x14370, 0x143a4)`: a table-bit gate and command ordinal filter. It depends on the original dispatcher frame and unconfirmed table and command contracts; it is not independently callable.

The builder and conditional-link verifier compile and link the fragment at its original address in both C and C++, checking the section, symbol, eight relocations and byte equality with the existing source carrier. This comparison is not independent proof of behavior. The 202-file isolated build passed, including its conditional-link failure control. Both 76,800-byte outputs have SHA-256 `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`. Of the 3,128-byte carrier, 716 bytes are compiled from source and 2,412 remain opaque.

Installed ROM, RAM ownership, runtime behavior and flash safety remain unproved; do not flash these outputs.
