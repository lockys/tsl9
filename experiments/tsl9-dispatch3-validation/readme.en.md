# Dispatcher buffer checks

Assuming the earlier 76-byte allocation and copy complete normally, the pointer is valid and address arithmetic does not wrap, `0x142C0` passes 14 bytes at offset `[4,18)` to a function. The subsequent loop at `0x142DA..0x142EA` reads bytes at offsets `[36,40)`; both intervals fit within 76 bytes. The loop branches to `0x14A1E` on the first byte outside 32–126, so all four bytes need not be read.

Both identified normal paths, completing that loop or exiting early, reach `0x142EE` and request a call through `0x40068` with the allocation pointer before branching on the saved result. The pinned WCH V1.31 header declares that slot as `tmos_msg_deallocate`. This does not prove actual release, successful allocation/copy, or release on other paths or exceptions. The 14-byte callee's effects, physical memory, resident/IRQ and stack remain unproved.

The [model](validation.c) accepts only a synthetic function return and four synthetic bytes; it does not perform the underlying validation or release. Windows MSVC C11 and C++17 each pass 2,048 cases; `verify_instructions.py` checks 20 instructions, the WCH reference slot and bounds arithmetic. The model is not integrated into the candidate BIN, and no device data is read or firmware executed.
