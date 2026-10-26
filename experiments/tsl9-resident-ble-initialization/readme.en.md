# BLE initialization and heap candidate C/C++

[繁體中文](README.md) · [Heap initialization](../tsl9-resident-heap-initialization/readme.en.md) · [Allocation/release](../tsl9-resident-heap-core/readme.en.md)

Three complete bodies from public WCH SDK V1.31 are reconstructed here. **Installed ROM/ISA identity remains unproved; this is not flashable firmware.**

| Body | Address domain and range | Bytes |
| --- | --- | ---: |
| Task initialization | Flash `0x43B3E..0x43C4E` | 272 |
| BLE_LibInit | Flash `0x43C7E..0x43D62` | 228 |
| tmos_memset | Conditional RAM `0x2000039C..0x200003CA` | 46 |

[Source](resident_ble_initialization.c):**546 bytes/193 instructions**,49 positive FUNC regions and39 relocations. Actual C11/C++17 objects are identical; every byte matches after original-address encoding. There are23 explicit conditional Xwchc byte/halfword ports,checked against primary definitions and28 official vectors. The adjacent independent function `0x43C4E..0x43C7E` is excluded.

## Evidence and limits

- Original APP code at `0x19A3A` encodes MEMAddr=`0x2000418C`,MEMLen=`0x7000` (28 KiB),and numerical end=`0x2000B18C`. This declares an arena;it does not prove physical RAM capacity or ownership.
- APP call `0x19AEC` uses pointer slot `0x400A4`,whose SDK candidate target is `0x43C7E`. Actual candidate direct calls connect `0x43D4C →0x43B3E` and `0x43B88 →0x43104`. The installed device ROM has not been measured.
- The64-byte configuration places staCB at offset52 (stack+68..72). All14 explicit field stores,the6-byte MAC helper output and the MAC copy avoid it. However,the opaque tsCB call at `0x43D38`,IRQ effects and alias ownership remain open;staCB being zero at heap allocation is unproved. No physical MAC/UID value was read.
- A task allocation-null instruction path restores and returns;after a normal task return,the outer entry forces numeric0. Runtime feasibility under valid configuration was not tested or proved. **Numeric0 alone is not proof of complete initialization.**

## Actual partial composition

With the preceding heap/message functions,initializer and copy body,the actual C/C++ nonloadable ET_REL objects contain **1336 bytes/467 instructions**,116 positive FUNC regions and86 relocations. Every input byte,symbol and relocation is retained.

Real copy,heap allocation and heap initialization definitions resolve three new imports. Three named functions remain unresolved (`0x200004BC`,`0x4329A`,`0x44022`),along with raw RAM,callback and callback-table CODE-address dependencies. This has not been linked into the APP or linked for execution at original addresses.

See [audit-result-v2.json](audit-result-v2.json),[summary.json](summary.json),[instruction/vector evidence](evidence-v1.json) and [original-header ABI assertions](config_abi.c). Formal APP byte coverage remains **95.54%**,not feature completion.

## Reproduce

First provide the original APP,SDK carrier,header and instruction references listed in [spec-v1.json](spec-v1.json) and [evidence-v1.json](evidence-v1.json). Original SDK reference inputs are not supplied by this commit. The audit also requires retained preceding candidate/curation artifacts;it does not download or regenerate them. Use the pinned Windows NDK LLVM tools. From the project root,set LLVM_BIN and use fresh trial names:

```sh
python experiments/tsl9-resident-ble-initialization/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-ble-initialization/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

For retained artifacts,use `--replay experiments/tsl9-resident-ble-initialization/build/native-v1` instead of the first trial option,and omit `--link-trial` from the second command. No target/HOST model/ISA execution,hardware access or new BIN occurs.

Startup allocation-completion and heap diagnostics are feature candidates only,pending installed RAM,callback/IRQ ownership and actual completion conditions.
