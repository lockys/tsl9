# OTA replies, cleanup and restart paths

[繁體中文](README.md) · [C/C++](../../src/native/receive/ota_replies.c) · [Original instructions](evidence.json) · [Summary](summary.json)

Six complete original functions add334B/127 instructions,29 private regions and18 control relocations. C11/C++17 objects agree. Six pending entries now have genuine implementations; two downstream dependencies16E0C/9EA6 are exposed, reducing unresolved providers77→73.

| Original range | Confirmed static behavior |
| --- | --- |
| 8E18–8E6A | Reads GP+150/154 halfwords,compares0xFFFE,uses original ROM slot0x4017C and retains the16B frame/tail paths. ROM purpose remains unproved. |
| 99E8–9A24 | Calls1917E twice and16E0C twice,clearsCSR0x800 bits0x88,writes0xE000E048,and loops at9A22. Reset-request-shaped; physical effect unproved. |
| 9B8E–9C0A | Original32B frame; requests1026B through ROM slot0x40070,returns on null,places a two-byte page index,copies1024B from the original page address,calls8A56,then releases through0x40068. No new page guard is invented. |
| 9EE0–9EF0 | Calls9EA6 with1,restores its frame,and tail-jumps99E8 with0.9EA6 remains unimplemented; persistence is not inferred. |
| 13E98–13EB4 | Tail-jumps13B4C when bothA2/A3 are nonzero,otherwise8A56; A6/A7 staging and all arguments retained. |
| 13F66–13F7E | Places low8(A2) at originalSP+15,passes length1 to13B4C,and restores its32B frame. |

Correction:8E66 jumps directly to8E4A JR T1,skipping8E48 SP+=16. The earlier report incorrectly included the skipped instruction; no stack imbalance is established by that branch. Source and original bytes were already correct and are unchanged. Physical caller/ROM ABI remains unproved. Prior report bytes are retained locally; the earlier final receipt is a historical snapshot.

The component contains20042B code+714B data; all20756B match the official ID2966 BIN after native original-address placement.112 C/H files and85 code units pass172 source comparisons/344 objects including independent pointer data. Previous111 sources and1009 artifact records remain unchanged.

Static flow covers6964 instructions,1146 direct transfers(1072 measured targets/74 reference-only),6422 ordinary next positions with no gaps,and425 potential call-return positions.361 register-indirect transfers,10MRET and1EBREAK remain outside a complete runtime CFG proof.

Initial component-v1 was rejected because its configuration counted three already-defined functions as new imports. The inventory was corrected and a fresh component-v2 passed; the failed artifacts are retained and no guard was loosened.

E is reply evidence,not a completed restart/functionality check. BOOT/APP roles,physical aliases,ROM/RAM/IRQ and OTA compatibility remain unproved. Diagnostic ELF entry0/PT_LOAD0 is not flashable. No target/HOST-model/ISA execution,hardware or network actions occurred. Historical privacy findings keep commit/push held.

Next: reconstruct16E0C/9EA6 and establish the remaining ROM/caller contracts. A proposed offline image-region/completion-stage inspector could distinguish reply,readback,cleanup and reset evidence while retaining original identifier/state checks; it is not implemented.
