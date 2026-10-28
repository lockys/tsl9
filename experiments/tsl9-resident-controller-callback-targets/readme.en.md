# Callback target bodies and conditional registration/dispatch provenance

[繁體中文](README.md) · [Project](../../readme.en.md) · [C/C++ candidate bodies](resident_controller_callback_targets.c)

**Three whole original bodies add258 CODE bytes /86 instructions.** C11/C++17,15 control relocations and complete CFG/frames match. The actual ordinary561B8 dependency resolves: **19 normal UND become18**. Two other new bodies are the earlier numeric callback targets,not two ordinary-import resolutions.

|Whole range (exclusive end)|Static evidence|
|---|---|
|55C32..55C48,22B/7 instructions/frame0|Null record returns;otherwise ORword160 with0x80 and writes255 toslot38|
|56CB2..56CDC,42B/16 instructions/frame16|Null returns before the frame. Call568F6 with original record and34,store its low-byte result at43,clearbyte16 and writeslot39=255|
|561B8..5627A,194B/63 instructions/frame16|Retain43E6A(0,4) initial halfword86 and original list/high multiply/REMU/truncation/candidate-step2 logic;product semantics and live domains remain unproved|

A further **1,014B/372 instructions** of existing whole references cover two slot wrappers,registration43874,two dispatchers and the561B8 caller. **None is counted as new CODE.**

43874 scansslots16..47 in12B entries throughglobal2000322C. Only after43728 returns nonzero does it store callback atword0,record atword4,and optionally a slot ID throughA3. Original returns are success0,null callback2,exhaustion8. Dispatchers use`12*((task<<4)+event_bit_index)`,loadword4 intoA0 and indirectly callword0. Thus **successful registration,matching event and unchanged valid table/record** conditionally connect the earlier numeric55C32/56CB2 arguments to their new bodies. The call at43390 has no local pointer-null guard;none is invented here.

**This proves original CODE identity and conditional argument provenance only.** Existing LUI/ADDI numeric pointers have no new native relocation. Final original-address placement,live table identity/immutability,callback lifetime and physical event delivery remain unproved;runtime binding is incomplete.

Identical C/C++ partial links contain **54,780 CODE+412 DATA bytes /18,917 instructions**,4,091 positive FUNCs,3,253 relocations and18 normal UND,without duplicate original CODE. All3 unit imports resolve to actual prior providers. No new DATA,stubs,aliases or own indirect calls;inherited dynamic callback gaps remain.

**No new BIN,formal src curation,APP integration or final original-address placement.** Formal APP stays162 sources/73,478 of76,800B (95.67% static byte coverage,not functional completion). Physical ROM/RAM/IRQ/Flash/OTA and the4B startup-source gap remain unproved. No target,HOST model,ISA or hardware execution and no vendor API access occurred.

[`verification-v1.json`](verification-v1.json) · [`summary.json`](summary.json) · [Unimplemented registration/callback diagnostic candidate](feature-candidates.json)

With frozen local inputs and LLVM,read-only replay:

```sh
python3 experiments/tsl9-resident-controller-callback-targets/verify-v1.py --tool-dir "$LLVM_BIN"
```
