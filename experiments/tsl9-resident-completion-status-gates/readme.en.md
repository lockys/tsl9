# Completion bit gates and counter updates

[繁體中文](README.md) · [Project](../../readme.en.md) · [C/C++ bodies](resident_completion_status_gates.c)

**Five whole original functions add246 CODE bytes /86 instructions.** C11/C++17 match all original instructions,9 control relocations and whole CFGs. No new normal imports,indirect calls or DATA. Actual bodies resolve5 parent normal UND: **20 become15**. Historical`unprovided` symbols now have actual definitions,without stubs or aliases.

|Whole range (exclusive end)|Static evidence|
|---|---|
|56086..560AA|Decode throughrecord+276:low2bits to+13;type3 readsbyte2 to+23,otherwise255;rawbit0x10 to+18 andbyte1 to+22|
|560B2..560D4|Different input header0 bit2 andrecord flags12 bit3:toggle record bit3,return0. Equal:return1 without toggle|
|560D4..560F6|Equal input header0 bit3 andrecord flags12 bit2:toggle record bit2,return0. Different:return1 without toggle|
|560F6..56146|Increment lowword228,carry to232 only when low becomes0. If high bit7 is set,resetlow1/high0. Conditionally updatehalfword70 and clearword164 bit10 underrecord42 bit6|
|56146..56184|Preserve corresponding carry/reset forwords236/240;conditionally setrecord42 bit5 underbit6|

The existing complete caller at **59800 calls560B2**. Return0 is only one condition before the queue-head update5983C;separate status/head/prepared/marker and release gates remain. Actual partial links retain the original call role and now own the complete positive CODE provider. The old role was already normalized to a CODE coordinate;**that coordinate label did not mean the body was previously implemented**.

These are numeric bit/branch/read-write facts,**not physical ACK/CRC,counter semantic or atomicity proof**. The decoder retains two distinct header0 reads,without merging snapshots or inventing a null guard. Valid record/input spans,IRQ/DMA coherence and lifetime remain conditions.

Identical C/C++ partial links contain **50,538 CODE+412 DATA bytes /17,547 instructions**,3,729 positive FUNCs,2,980 relocations and15 normal UND,with no duplicate original CODE. Parent bytes,globals and relocation roles remain. This candidate is not curated into formal src,linked into APP or finally placed at original addresses.

Formal APP remains **162 sources /73,478 of76,800B (95.67% static byte coverage)**,not functional completion. **No new BIN or proved physical ROM/RAM/IRQ/Flash/OTA compatibility.** The4B startup-source and inherited indirect/RAM gaps remain. No target,HOST model,ISA or hardware execution and no vendor API access occurred.

[`verification-v1.json`](verification-v1.json) · [`summary.json`](summary.json) · [Unimplemented diagnostic candidate](feature-candidates.json)

With frozen local inputs and LLVM,read-only replay:

```sh
python3 experiments/tsl9-resident-completion-status-gates/verify-v1.py --tool-dir "$LLVM_BIN"
```
