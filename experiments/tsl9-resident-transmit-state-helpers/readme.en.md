# State helpers and fragment-limit producers

[繁體中文](README.md) · [Project](../../readme.en.md) · [C/C++ bodies](resident_transmit_state_helpers.c)

**Twelve whole original helpers add682 CODE bytes /257 instructions.** C11/C++17 match original instructions,29 control relocations and whole CFGs. Actual bodies resolve12 parent normal imports: **42 UND become30**, with no new normal imports, indirect calls or DATA. Historical`unprovided` symbol names now have actual definitions to preserve existing references;no stubs or aliases were added.

|Whole entry|Static evidence|
|---|---|
|5A1DC,5A222,5A23E,5A25E,5A286,5A306,5A326,5A348,5A370|Update length atrecord+21 before testing frame pointer+272. Null returns7 or1 retain that side effect. Normal paths prepare numeric opcodes2/6/7/10/11/13/17/18/19|
|5A2A2..5A306|Prepare opcode12 using loads atglobal base200033B8 offsets20/22/24/25. Preserve conditional flag changes atrecord+46,+43,+160. Live global values were not observed|
|5A386..5A406|Prepare opcode22;derive a candidate fromrecord+324 flags and halfwords+486/+328, take unsigned min withhalfword+484 and store the low byte at+78|
|5A48E..5A52A|Prepare opcode24;retain`uint16(counter64+8)` atrecord+332 and optional header counter,then derive/store the corresponding limit atrecord+78|

The last three bodies have **no local null-buffer guard**. Valid records and frame buffers remain preconditions. Both limit calculations retain signed DIV,arithmetic shifts,uint16 truncation,unsigned comparison and final byte truncation. Do not replace them with unsigned arithmetic or invented allocation clamps. These are two actual producers of the prior fragment preparer'srecord+78 input. **Live input ranges and its bound against allocated frame size remain unproved**,as do protocol names for the numeric opcodes.

Identical C/C++ partial links contain **49,402 CODE+412 DATA bytes /17,140 instructions**,3,657 positive FUNCs,2,942 relocations and30 normal UND,with no duplicate original CODE. Parent bytes,globals and relocation roles remain. This candidate SDK object is not curated into formal src,linked into APP or finally placed at original addresses.

Formal APP remains **162 source files /73,478 of76,800B (95.67% static byte coverage)**,not functional completion. **No new BIN or proved physical ROM/RAM/IRQ/Flash/OTA compatibility.** The4B startup-source and inherited indirect/RAM gaps remain. No target,HOST model,ISA or hardware execution and no vendor API access occurred.

[`verification-v1.json`](verification-v1.json) · [`summary.json`](summary.json) · [Unimplemented diagnostic candidate](feature-candidates.json)

With frozen local inputs and LLVM,read-only replay:

```sh
python3 experiments/tsl9-resident-transmit-state-helpers/verify-v1.py --tool-dir "$LLVM_BIN"
```
