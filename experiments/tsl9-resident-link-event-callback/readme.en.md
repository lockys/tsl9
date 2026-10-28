# Connection-event callback and pending-record cleanup

[繁體中文](README.md) · [Project](../../readme.en.md) · [C/C++ bodies](resident_link_event_callback.c)

Fourteen complete archived SDK bodies add **1,068 CODE bytes/428 instructions**. C11/C++17 native objects match original instructions and82 relocations. Register bindings,volatile accesses and necessary inline assembly retain the original-layout/ABI requirements.

|Location|Confirmed static behavior|
|---|---|
|`0x4D916..0x4D952`|Ignore loopback handleFFFE before adding a frame. Event1 tails to cleanup with reason0;event2 queries connected bit1 and cleans only when false;other events return|
|`0x4F072..0x4F0A4`|Loopback returns true;missing link record returns false;otherwise test the flag byte atrecord+4 and return a boolean|
|RAM `0x20000A94..0x20000AC6`|Conditional Flash source0x40D04..0x40D36;sample total once,find the first60B record matching handle+2,or returnNULL|
|`0x4D83A..0x4D916`|Scan16B pending records using live counts. Reason0 also runs the second cleanup group and resource indices4..7;retain fresh reads and matching guards|
|`0x4D66E..0x4D6BA`|For a nonnull nested owner,conditionally release children+12/+20 in order,then the owner;clear16B and setslot9 toFF|
|`0x4D820..0x4D83A`|Passslot9 to the existing candidate record-removal helper43A14,then setslot9 toFF;no physical timer-state inference|
|`0x4E2EE..0x4E362`|Allocate32B;NULL returns without sending. Copy or zero the24B body at+8,then frame-release tail to the existing message sender|
|`0x4EBC2..0x4EBDA`|24B/12-instruction serializer callback rereads two halfwords,writes four little-endian bytes and returns4;fresh reads are not coalesced|

Previously,callback0x4D916 existed only as a literal address. Its complete candidate body is now supplied. A second literal0x4EBC2 has its actual serializer body too. Both still require original-address binding;neither is an invented typed relocation or evidence of physical invocation.

Six normal imports resolve to existing release/fill/copy/message/record helpers. **0x4EB12 remains the sole named UND,with no invented body.** The cleanup path is not closed,and actual CCC clearing or OTA repair is unproved. Complete stack-payload initialization is also unproved;unproven bytes are not silently replaced with zero.

Identical actual C/C++ partial compositions contain **43,350 CODE+412 DATA bytes/15,020 instructions**,3,048 positive FUNCs,2,435 relocations and one named UND. Every parent allocated byte,global and typed role is retained. The serializer extension is receipted in `native-v2`;the thirteen-body `native-v1` remains local.

Formal APP provenance stays **162 files/73,478 of76,800B（95.67% static byte coverage）**,not functional completion. SDK code is not linked into the APP or finally placed at original addresses. The inherited4B startup-source gap remains. **No new BIN or physical ROM/RAM/IRQ/Flash/OTA compatibility proof.** No target,HOST model,ISA or hardware execution and no vendor API access occurred.

[`verification-v1.json`](verification-v1.json) · [`summary.json`](summary.json) · [Unimplemented offline diagnostic candidate](feature-candidates.json)

With frozen local inputs and LLVM,read-only replay:

```sh
python3 experiments/tsl9-resident-link-event-callback/verify-v1.py --tool-dir "$LLVM_BIN"
```
