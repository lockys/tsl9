# Dispatcher copy and scheduling continuation

`src/native/receive/ota_dispatch_1432e.inc` reconstructs 66 bytes at `[0x1432e, 0x14370)`. It copies two 16-byte regions via resident slot `0x4004c` and calls `0x13138`, `0x9124` and `0x13dd4`. It depends on the original dispatcher frame and unconfirmed table, resident and scheduling contracts; it is not independently callable.

The builder and conditional-link verifier compile and link the fragment at its original address in both C and C++, checking section, symbol, three relocations and byte equality with the existing source carrier. This comparison is not independent proof of behavior. The 201-file isolated build passed, including its conditional-link failure control. Both 76,800-byte outputs have SHA-256 `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`. Of the 3,128-byte carrier, 664 bytes are compiled from source and 2,464 remain opaque.

Installed ROM, RAM ownership, runtime behavior and flash safety remain unproved; do not flash these outputs.
