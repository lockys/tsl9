# Status callback dispatch,link removal and request core

[繁體中文](README.md) · [Project](../../readme.en.md) · [C/C++ bodies](resident_link_dispatch_core.c)

Fourteen whole archived SDK bodies add **1,260 CODE bytes/495 instructions**. C11/C++17 match original instructions and100 relocations. Register bindings,volatile accesses,conditional Xwchc and necessary inline assembly retain original-layout/ABI requirements.

|Evidence|Confirmed static behavior|
|---|---|
|`0x4ED98..0x4EDD2`|The actual12-slot status dispatcher fresh-loads0x20003358..0x20003388,skips NULL holes,and forwards the original handle/changeType to nonnull callbacks|
|`0x4F00C..0x4F058`|Missing record returns2. Otherwise dispatch event1 before guarded release ofrecord+44,clear60B,sethandleFFFF/state0,and return0|
|`0x4F0CC..0x4F128`|A separate per-link iterator,with a pre-frame null-callback return,fresh total/pointer loads and60B record-pointer arguments. Its whole entry is4F0CC;it is not the status dispatcher|
|`0x4EB12..0x4EBC2`|176B request core:selector6 looks up an existing record,other paths allocate;retain transaction-byte increment/zero skipping,error cleanup and numeric delay30 after zero return|
|`0x4D4BC..0x4D5A0`|Null out pointer returns1,not-connected20,no slot/heap21. Preserve32B nested allocation and both original shifts rather than an inferred index formula|
|`0x4D806..0x4D820`,`0x4D6E0..0x4D70A`|Multiply numeric delay by1600 and schedule literal4D6E0;nonnull/nonzero-key callback usesstatus23 and a frame-released cleanup tail. Physical time units remain unproved|
|`0x4EA8C..0x4EB12`|Save and indirectly call the serializer;write selector,transaction and length fields with numeric channel5. Source,length and callback validity remain conditions|
|RAM `0x200001E4..0x2000021C`|Conditional source40454..4048C;adjust a buffer pointer under heap-chain range checks,or preserve the original pointer. Live-chain validity/termination remain unproved|
|`0x534A6..0x534AA`|One4B tail jump to6A626;adjacent functions are not counted|

**Conditional invocation chain:** if nonzero-total initialization completes48B zero-fill and the table remains stable through first-empty registration/dispatch,the first slot receives literal4D916. Its stable dispatch iteration calls that body with the saved original handle/changeType. The removal path then reaches the previously rebuilt reason0 cleanup. This is original-candidate CFG/dataflow evidence,not physical invocation or global lifetime proof.

0x4EB12 retains its historical import name but now has its actual176B source body,no empty alias. Ten new imports resolve to real prior providers. **0x6A626 is the sole named UND.** Three indirect sites still have unclosed possible runtime targets,and literal callbacks need original-address binding. UND count alone is not runtime closure.

The selector6 path requires a validrecord+12 nested pointer before its unguarded halfword read;no invented null guard is added. Numeric statuses,channel5 and delay multipliers do not establish protocol completeness,physical timing or OTA diagnosis.

Identical actual C/C++ compositions contain **44,610 CODE+412 DATA bytes/15,515 instructions**,3,175 positive FUNCs,2,535 relocations and one named UND. Parent allocated bytes,globals and symbolic relocation roles remain;the prior UND now resolves to genuine CODE.

Formal APP provenance stays **162 files/73,478 of76,800B（95.67% static byte coverage）**,not functional completion. SDK code is not linked into the APP or finally placed at original addresses. The inherited4B startup-source gap remains. **No new BIN or physical ROM/RAM/IRQ/Flash/OTA compatibility proof.** No target,HOST model,ISA or hardware execution and no vendor API access occurred.

[`verification-v1.json`](verification-v1.json) · [`summary.json`](summary.json) · [Unimplemented offline diagnostic candidate](feature-candidates.json)

With frozen local inputs and LLVM,read-only replay:

```sh
python3 experiments/tsl9-resident-link-dispatch-core/verify-v1.py --tool-dir "$LLVM_BIN"
```
