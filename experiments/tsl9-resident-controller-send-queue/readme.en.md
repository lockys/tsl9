# Controller enqueue and descriptor pool

[繁體中文](README.md) · [Project](../../readme.en.md) · [C/C++ bodies](resident_controller_send_queue.c)

Two whole archived SDK bodies add **284 CODE bytes/101 instructions**:controller enqueue0x6A626..0x6A700（218B/79 instructions）and pool lookup0x57862..0x578A4（66B/22 instructions）. C11/C++17 native objects match original instructions and18 relocations,retaining register bindings,volatile accesses,FENCE.I,variable SLL and conditional Xwchc.

|Evidence|Confirmed static behavior|
|---|---|
|`0x6A63A..0x6A670`|Missing connection returns2. Zero length sets shared flag20002FA8 and returns0. The next valid nonzero request withflag1 clears it and overrides the incoming argument with2|
|`0x6A676..0x6A67E`|Save4002420C,write0 and executeFENCE.I;all later normal-return paths include a matching restore. Physical register/IRQ meaning remains unproved|
|`0x57862..0x578A4`|Use BufNumber/mode to scan16B nodes for the firstFF54 orFFFF tag. There is no global exact-match preference. This is not a heap allocator|
|`0x6A68E..0x6A6B4`|LBU node+10 then SH the result at the same offset;link queue head/tail atconnection+280/+284,storeincoming pointer−2,length halfword+12,andmarker+9=0x81|
|`0x6A6B6..0x6A6D2`|Form `low16(1 << (slot&31))` fromrecord+41,request a task0 event,ignore its return and return0. This is not radio-delivery proof|
|`0x6A6DC..0x6A6FA`|Pool miss may invoke staCB(1,0x5555) while the control word is still zero;after normal callback return,restore and return7|

Whole references also check the existing190B pool initializer,308B APP configuration initializer and228B BLE_LibInit against actual native artifacts. Pool base is20003464;count is `mode==0 ? c+1 : 2*c`. The APP nominal BufNumber8 conditionally gives9 or16 nodes if preserved. Allocation,16-bit size truncation,fresh post-call count and initialization order remain conditions;live RAM extent is not proved.

Official compile-only layout assertions establish BufNumber offset15 andstaCB offset52. The APP clears64 config bytes with no later explicit stack store tostaCB,and the library copies64B. If no intervening/later overwrite occurs,staCB isNULL and this error callback is skipped. This conditional result does not close every possible live callback target.

The prior0x6A626 import now has its actual218B body,no empty alias. Both new normal imports resolve to real prior lookup/event providers. Identical C/C++ compositions contain **44,894 CODE+412 DATA bytes/15,616 instructions**,3,203 positive FUNCs,2,553 relocations and **zero named normal UND**. Parent bytes,globals and symbolic relocation roles remain.

Zero UND is not runtime closure. Indirect callbacks,global lifetime,pool/heap chains,head/tail consistency,payload prefix,MMIO semantics,task consumption and radio delivery still require evidence. Enqueue success is not OTA success;no invented pointer guard or retry was added.

Formal APP provenance stays **162 files/73,478 of76,800B（95.67% static byte coverage）**,not functional completion. SDK code is not linked into the APP or finally placed at original addresses. The inherited4B startup-source gap remains. **No new BIN or physical ROM/RAM/IRQ/Flash/OTA compatibility proof.** No target,HOST model,ISA or hardware execution and no vendor API access occurred.

[`verification-v1.json`](verification-v1.json) · [`summary.json`](summary.json) · [Unimplemented feature candidate](feature-candidates.json):after compatibility validation,consider read-only aggregate queue/pool health diagnostics.

With frozen local inputs and LLVM,read-only replay:

```sh
python3 experiments/tsl9-resident-controller-send-queue/verify-v1.py --tool-dir "$LLVM_BIN"
```
