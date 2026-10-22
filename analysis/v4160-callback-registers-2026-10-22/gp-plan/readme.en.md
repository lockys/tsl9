# Why read live GP directly

[繁體中文](README.md)

The actual 656-byte S10/S11-reserved component with the old snapshot bridge contains sixteen `C.MV rd,GP` instructions: one at entry and one after each of fifteen opaque calls, totaling32 bytes. `first-fixed-GP-copies.json` reads their source fields from actual ELF halfwords rather than inferring instructions from text search.

This observation alone does not justify deleting instructions. The old bridge snapshots GP into a C field. The new source must read the current physical GP at the six real uses before removing unused native snapshots. It must not assume callee GP preservation or reuse a pre-call scalar. The six HOST accessors must still select the same original mutable field. Historical HOST results remain separate from new native evidence.

Six uses cover two context-byte reads, lane-relative connection-halfword addressing, two GP+128 arguments and a GP+42 halfword read followed by a descriptor store. Source and independent ABI reviews check volatile register-read IR, actual widths, no GP writes and ordering around opaque calls. Clang lowers the last LHU to LH; the subsequent low16 store can correspond, but physical intermediate GPR sign prefixes are not identical.

This improves readable C/C++ and its narrow physical-register bridge. It executes no original firmware or CPU model, connects no hardware and uses no device identity. Installed ROM/BOOT, full ABI and BLE OTA remain unproved.
