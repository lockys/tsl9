# Record dispatcher 12A08
[繁體中文](readme.zh-TW.md)

Reconstructs official V4.1.60 `[0x12A08,0x12A6E)`:102B/35 instructions across nine private architectural regions. C arithmetic uses explicit frame/register/access/control ports; regions are not independent ordinary C ABI functions. Selected source: `src/record_dispatch.v2.c`; curated copy: `src/native/receive/record_dispatch.c` at repository root.

Preserves the48B frame, status/ID/predicate/tag paths, SP+20→SP+12→SP+22 metadata stores, unwritten SP+16..19, fresh [0x4004C] indirect call, then-live SP/S0/A2/A3 residues, four original4B JAL return addresses and post-RET tagged path. Names do not establish memcpy, CAN, or successful transmission.

One fixed RV32IMAC_Zicsr/ILP32/Oz profile builds C11 and C++17. Source v1 failed because four JALs compressed; v2 only constrains their architecture ports to original4B form. [source-history.json](source-history.json) retains failures. Each formal `build/verified-v1/{c,cpp}/verification.json` passes212 negative controls, complete IR/SSA/CFG, MD, five actual recipes, ELF and689 original retained bits. Nine pending RELAs/four genuine UND remain. Public portable receipts retain original bytes; raw logs remain local.

From repository root, with existing LLVM:
```sh
python experiments/tsl9-record-dispatch/verify.py --language c --out-dir experiments/tsl9-record-dispatch/build/verified-NEW/c --llvm-bin "$LLVM"
python experiments/tsl9-record-dispatch/verify.py --replay experiments/tsl9-record-dispatch/build/verified-v1/c/verification.json --llvm-bin "$LLVM"
```

Static proof only; no RV32/MMIO/hardware execution. `--require-firmware-ready` must reject. Placement, resident/provider ABI, ROM, IRQ, memory and OTA compatibility remain open; this is not a flashable BIN.
