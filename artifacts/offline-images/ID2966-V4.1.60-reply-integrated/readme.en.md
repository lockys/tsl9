# Twelve-function offline rebuilt image

[繁體中文](README.md)

`NOT-FLASH-VALIDATED-reply-integrated.bin` is a complete 76,800-byte offline
image, SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.
Its contents match official ID2966 V4.1.60's original decoded image.

Readable C/C++ covers twelve IRQ/Flash/OTA page-reply functions, totaling
650 bytes. The remaining 679 sections still use original carriers; this is
partial source recovery. The pipeline compiles 34 carrier and nine readable
translation units and emits nine IR files. Its 61 actual commands comprise
59 LLVM operations and two explicit ABI-ordering operations. Both backends
only reorder existing newly compiled words. There is no original-BIN
generation input, padding, fallback or compiler-only final-order claim.

Every compilation records full `-MD` dependencies, including actual Clang
resource-header identities. Source and artifact checks cover retained bytes,
all 691 allocations, 8,269 relocations, 53 relative bindings, 21 incoming
entries and fifteen LOADs' full file/memory extents and permissions. The reply
preserves its original public NOTYPE / size 0 and local entries; the incoming
instruction at `0x9DF4` remains a linking `C.JAL`.

Strict linking still rejects the absent ROM implementation. Successful
linking uses `0x40000` only as a numeric-address witness, without ROM contents
or version proof. Byte identity alone cannot identify the physical TSL9 board,
installed BOOT or exact file previously updated successfully by the user.

**Not verified as flashable.** This is not new-feature firmware, physical OTA
testing or recovery evidence. No RV32 execution/emulation, BLE/CAN/UART
connection or hardware flashing was performed.

Sources, receipt metadata and reproduction instructions are in the
[integration evidence](../../../analysis/v4160-reply-image-integration-2026-10-22/readme.en.md).
Source, metadata, actual artifact replay, fresh compilation and physical
hardware remain separate evidence levels.
