# Five-entry relative jump table in the 0x14056 dispatcher

[繁體中文](README.md)

The consumer of a previously speculative table is now identified: `0x144C2..0x144C6` branches to `0x14512` for command `0xD0`. It reads the first byte at `s0` and exits if the unsigned index exceeds 4. For indexes 0–4, `0x1451C..0x1452C` reads five signed 32-bit relative offsets based at `0x1A6A4` and jumps indirectly.

The destinations are `0x1452E`, `0x1453E`, `0x1454A`, `0x1473E` and `0x14748`; all are decoded instruction boundaries in the original section. The former candidate interpretation based at `0x1A6A0` was not the actual consumer base; the preceding word is outside this five-entry table. This relies on normal control flow, a valid `s0`, stable memory and the assumed instruction set; it does not establish actual reachability of all indexes or product semantics.

Run `python scripts/verify-payload-jump-table.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>`. Both C/C++ paths verify 12 key instructions, actual section backing for the table, all destinations, guard arithmetic for 256 byte values, and a mutated-table negative control. The target is not executed; installed ROM/RAM/OTA compatibility remains unproved.
