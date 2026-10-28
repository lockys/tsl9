# Completion tails,controller transitions and existing diagnostic callback

[繁體中文](README.md) · [Project](../../readme.en.md) · [C/C++ candidate bodies](resident_completion_chain.c)

**Three whole original bodies add3,204 CODE bytes /1,011 instructions.** C11/C++17 match original instructions,195 direct controls and5 far-call pairs (205 relocations),with complete CFG/frame checks. This reconstructs original instructions;many numeric state branches still lack proved product semantics.

|Whole range (exclusive end)|Confirmed original behavior|
|---|---|
|567BE..568D4,278B/92 instructions/frame32|Retain two indirect callbacks,record14=176 and both exit paths. One writes numeric addressE000E204;the other restores its frame before tail4354A,retaining RV32 shift anduint16 event-mask truncation|
|56D0E..5774E,2,624B/818 instructions/frame48|Retain the complete multi-flag transition body,post-return arms and seven indirect sites,including conditional numeric statuscodes9–12|
|58F14..59042,302B/101 instructions/frame32|Retain record310-indexed bitmap testing,first clear-bit set-and-return path,two flag guards,5B copy torecord296 and word164 flag changes|

Original completion calls **59BC0/59C3C→56D0E,59BFA→58F14,andtail59C14→567BE** preserve the original record argument. The tail restores its caller frame. Partial links retain these roles with actual positive original CODE providers;coordinates or stubs are not counted as implementation.

The official header declares`staCB` as`void(uint8_t code,uint32_t status)` atconfig offset52. Original56D0E reads it throughglobal20003220. Nonzero record64,modulo100,configuration-bit and initial-nonnull gates precede:

|code|Original numeric argument|
|---|---|
|9|Global200033B8 halfword16 in high16 bits,halfword18 in low16 bits|
|10|The same global'shalfword14|
|11|Sign-extended record halfword50|
|12|Sign-extended record byte52|

**Only the first pointer has a null guard;later calls reload the pointer.** Its validity after a preceding callback remains a condition. Original cache clearing on dispatch or the corresponding config/null-pointer arm remains. Physical value meanings,actual hardware enablement and any wall-clock interpretation ofmodulo100 are unproved. This existing interface is a worthwhile read-only diagnostic candidate,not implemented here.

Three old normal UND resolve. The unit has23 imports:13 resolve to actual parent providers and **10 new missing callees remain genuine**. Overall normal UND therefore changes from15 to**22**,plus **nine new open indirect sites**. No new DATA,stubs or aliases. Identical C/C++ partial links contain **53,742 CODE+412 DATA bytes /18,558 instructions**,3,997 positive FUNCs and3,185 relocations,without duplicate original CODE. Parent bytes,globals and relocation roles remain.

**No new BIN,formal src curation,APP integration or final original-address placement.** Formal APP stays162 sources/73,478 of76,800B (95.67% static byte coverage,not functional completion). Physical ROM/RAM/IRQ/Flash/OTA and the4B startup-source gap remain unproved. A numeric MMIO write does not identify the physical interrupt controller. No target,HOST model,ISA or hardware execution and no vendor API access occurred.

[`verification-v1.json`](verification-v1.json) · [`summary.json`](summary.json) · [Unimplemented diagnostic candidate](feature-candidates.json)

With frozen local inputs and LLVM,read-only replay:

```sh
python3 experiments/tsl9-resident-completion-chain/verify-v1.py --tool-dir "$LLVM_BIN"
```
