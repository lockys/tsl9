# Controller-state helpers,slots and numeric-pointer gaps

[繁體中文](README.md) · [Project](../../readme.en.md) · [C/C++ candidate bodies](resident_controller_state_helpers.c)

**Four whole original functions add780 CODE bytes /273 instructions.** C11/C++17 match original instructions,51 direct controls and1 far-tail pair (53 relocations),with complete CFG/frame checks. Four of5 unit imports resolve to actual parent providers. Four old normal UND resolve and one new561B8 import remains: **22 become19**,without stubs or aliases.

|Whole range (exclusive end)|Static evidence|
|---|---|
|55C6E..55CC4,86B/28 instructions/frame32|Ifslot38 differs from255,call43A14 then write255. Retain record42 OR0x60 and`uint16(record64+record72)` to70;restore the frame before tail43874|
|55CC4..55D00,60B/21 instructions/frame32|Corresponding conditional call/write forslot39,then restore the frame andtail43874|
|5649C..56574,216B/78 instructions/frame16|Retain global count/list andrecord29/11/140/28 gates,distinct record updates,and existing fill-helper tail onpeer+104,value255,length12 after frame release|
|56574..56716,418B/146 instructions/frame16|Retain complete list selection,REMU,signed/unsigned comparisons and truncation,including the new561B8 call and numeric record29 phases3/18/19|

Original controller calls **56E4C→55C6E,57414/57480→55CC4,574E0→56574,57748→5649C** retain original record-argument provenance under whole-CFG checks. Actual partial objects now own their complete positive original CODE bodies.

The43874 tails pass numeric55C32/56CB2,the original record,preserved incomingA1,and the address ofslot38/39. **Neither numeric target body nor typed CODE binding is supplied.** Do not count them as rebuilt callbacks or infer runtime closure from ordinary UND alone. Calling43A14 does not prove physical cleanup success.

Retain global2000346C count/global20003454 list references,record29 nonzero gates,record28 reset paths and numeric states1/2/3/18/19. Valid list/next pointers,divisor domains and IRQ/DMA/reentrant coherence remain conditions. Product meanings are unproved;no invented C arithmetic,clamps or forced phase transitions.

Identical C/C++ partial links contain **54,522 CODE+412 DATA bytes /18,831 instructions**,4,068 positive FUNCs,3,238 relocations and19 normal UND,without duplicate original CODE. No new DATA or own indirect calls. Inherited indirect gaps and both numeric pointers remain. Parent bytes,globals and relocation roles are retained.

**No new BIN,formal src curation,APP integration or final original-address placement.** Formal APP stays162 sources/73,478 of76,800B (95.67% static byte coverage,not functional completion). Physical ROM/RAM/IRQ/Flash/OTA and the4B startup-source gap remain unproved. No target,HOST model,ISA or hardware execution and no vendor API access occurred.

[`verification-v1.json`](verification-v1.json) · [`summary.json`](summary.json) · [Unimplemented slot/numeric-state diagnostic candidate](feature-candidates.json)

With frozen local inputs and LLVM,read-only replay:

```sh
python3 experiments/tsl9-resident-controller-state-helpers/verify-v1.py --tool-dir "$LLVM_BIN"
```
