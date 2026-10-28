# APP write callback,UUID and candidate CCC notification chain

[繁體中文](README.md) · [Project](../../readme.en.md) · [C/C++ CCC bodies](resident_gatt_CCC_write.c) · [Two-byte APP UUID](write_UUID.c)

Six complete archived SDK bodies add **274 CODE bytes/115 instructions**,plus the APP's actually read **two-byte UUID `0x1AB44..0x1AB46`（FFF1）**. C11/C++17 match original bytes/data and22 control relocations,with no new normal CODE imports.

|Location|Verified behavior|
|---|---|
|APP table `0x19DFC`|Readonly `[NULL,0x888C,NULL]`;no APP read/authorize callback.8614 is not this table's read callback|
|APP `0x888C..0x8A56`|Whole458B/153-instruction callback,64-byte frame and pre-frame exits;candidate permission bit32 returns8,and type/UUID/handle mismatches may return0|
|APP `0x88CE..0x88D0`|Load pointer fromGP+36,then read exactly2B usingLHU;conditionally1AB44,without inferring full-table extent|
|APP `0x88C8`|CCC UUID2902 path preservesA0..A4,setsvalidCfg1,and tail-calls slot40144→candidate4B4A4 without adding a frame or writingRA|
|SDK `0x4B2E4..0x4B308`,`0x4B33C..0x4B35A`|Look up four-byte records or clear handles toFFFF/value0 using the capacity byte;leave padding byte3 untouched|
|SDK `0x4B456..0x4B500`|Read/update/find a free record and process two-byte CCC writes;retain fresh lookups and frame-released tail|
|SDK `0x4CFD0..0x4CFF6`|FFFF tail-clears all records;other connections clear their matching record|

Nonzero offset returns11,non-two-byte length returns13,and unsupported configuration bits return128. The APP mask1 allows request values0/1 under the normal ABI. **This does not prove a physical subscription or delivered notification.** Unchanged values return0 without writing;missing-record reads return0,and writes with no free record return17. Zero is not always evidence of mutation.

Official candidate layout assertions allocate zero runtime bytes:handle halfword offset0,value byte offset2,stride4. APP `0x8FB6` suppliesFFFF andGP+128 to the candidate initializer,but the live capacity is read from `0x200033B5`. Its value/assignment order and RAM ownership remain unproved. Capacity0 touches no records. Each fresh sample requires a valid nonwrapping4×capacity table;do not assume two records.

Identical C/C++ partial compositions contain **41,684 CODE+412 DATA bytes/14,394 instructions** for the SDK,with2,917 positive FUNCs,2,317 relocations and no named UND. The APP experimental component has **69,412 CODE+4,068 DATA bytes**,retaining six UND and5,270 relocation roles. All parent allocations/globals/typed relations remain intact.

The two-byte UUID is not yet curated into `src/` or finally placed at original addresses. Formal APP provenance remains162 files/**73,478/76,800B（95.67%）**. No full-provider alias,router replacement or withheld payload/individual hash was selected. The inherited4-byte SDK startup-source gap remains. These statuses do not diagnose the earlier OTA letterE.

[`verification-v2.json`](verification-v2.json) and[`summary.json`](summary.json) retain whole CFGs,unique reaching definitions and native/independent-reader evidence. Installed ROM/Xwchc/ABI,global pointers/capacity/callback lifetime and physical RAM/IRQ/Flash/OTA remain open. **No new BIN or verified usable replacement firmware.** No target/HOST-model/ISA/hardware execution occurred.

With frozen local inputs and LLVM,read-only replay is:

```sh
python3 experiments/tsl9-resident-gatt-CCC-write/verify-v2.py --tool-dir "$LLVM_BIN"
```

Only text sources/evidence are committed;native outputs stay local. The[feature candidate](feature-candidates.json)is an unimplemented offline notification/CCC capacity diagnostic.
