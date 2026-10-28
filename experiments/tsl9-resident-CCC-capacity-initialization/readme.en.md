# CCC capacity initialization and APP call order

[繁體中文](README.md) · [Project](../../readme.en.md) · [C/C++ bodies](resident_CCC_capacity_initialization.c)

Four complete archived SDK bodies add **598 CODE bytes/198 instructions**. C11/C++17 objects match original instructions and36 relocations. Two normal imports resolve to existing allocator/memset bodies. Callback `0x4D916` remains unprovided: zero named UND does not establish a complete runtime.

|Evidence|Confirmed static behavior|
|---|---|
|APP `0x19A70`|SH stores0x0E3F atSP+36. Config starts atSP+16;ConnectNumber offset21 gives nominal0x0E|
|SDK `0x43CE8`|Copies64 config bytes to0x200031EC;offset21 is0x20003201|
|SDK `0x4EDD2..0x4EE72`|Reads that byte;writes `c&3` toCCC capacity0x200033B5 and `(c&3)+(c>>2)` to total0x200033B4|
|APP `0x8EB6` → PeripheralInit `0x6DD2A` → `0x4DACE`|Normal call progression initializes capacity before APP0x8FB6 clears CCC records|
|CentralInit `0x6DDB0`|Conditionally calls the common initializer;its skip branch is preserved|
|SDK `0x4EFE2..0x4F00C`|Registers in the first empty slot of a12-entry callback table;full table returns19,not a universal OTA diagnosis|

**Conditional inference:** if the APP byte remains0x0E through store,copy and helper read,CCC capacity is **two four-byte records/eight bytes** at0x20004080..0x20004088,total connections5,and candidate allocation300B. Local normal-CFG call order is established;live values,an exhaustive global writer set and physical RAM ownership are not.

The capacity store precedes allocation. **There is no allocator-null guard** before fill/dereference. Fresh total loads after calls remain intact. Zero total skips allocation and the48-byte callback-table clear. A completed capacity store does not prove successful table/callback setup. Normal ABI,returning callees,unchanged configuration and no alias/IRQ/DMA/reentrant interference remain conditions.

Whole references also cover APP main384B,configuration initializer308B,existing BLE_LibInit228B,and two role wrappers246B/66 instructions. The wrappers are whole raw CFG references,not newly supplied native providers.

Identical C/C++ partial links contain **42,282 CODE+412 DATA bytes/14,592 instructions**,2,950 positive FUNCs,2,353 relocations and no named UND. Every parent allocated byte,global and typed relation is retained. An inherited unprovided-callback flag was corrected and receipted in `native-v2`;the original `native-v1` stays local.

Formal APP provenance remains **162 files/73,478 of76,800B（95.67% static byte coverage）**,not functional completion. SDK code is not linked into the APP or finally placed at original addresses. The inherited4B startup-source gap remains. **No new BIN or physical ROM/RAM/IRQ/Flash/OTA compatibility proof.** No target,HOST model,ISA or hardware execution and no vendor API access occurred.

[`verification-v1.json`](verification-v1.json) · [`summary.json`](summary.json) · [Unimplemented offline diagnostic candidate](feature-candidates.json)

With frozen local inputs and LLVM,read-only replay:

```sh
python3 experiments/tsl9-resident-CCC-capacity-initialization/verify-v1.py --tool-dir "$LLVM_BIN"
```
