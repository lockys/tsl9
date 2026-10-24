# Original event callbacks and parameter carriers

[繁體中文](README.md) · [C/C++](../../src/native/receive/runtime_callbacks.c) · [Evidence](evidence.json) · [Summary](summary.json) · [Constant references](constant-reference-audit.json)

Three complete original functions add1072B/369 instructions. C11/C++17 outputs match original-address code. Previously literal-only8614/8C82 and existing8B6E now have genuine bodies;75 UND becomes72 with no new dependencies.

| Original range (exclusive end) | Confirmed static behavior |
| --- | --- |
| 8614–888C | Complete48B frame/RA/S0–S9; dispatch on signed low16(original A1) and event bits; preserve GP+148/152 selection,1062B buffer stride and ROM calls. All paths after firstRET8684 retained. |
| 8B6E–8B90 | Preserve32B frame; low8(original A0) atSP+15; word[0x40174] receives(773,1,SP+15). |
| 8C82–8E18 | Complete48B frame; ordered flag1/2/4/8/16/32 paths,including after firstRET8CB6. Flag2 constructs26 local bytes with fixed TSL9 text,GP+140 counter and GP+145 value,then submits(774,26,SP+4) to the ROM slot. |

An advertising-style payload is an inference,not observed radio transmission. ROM semantics,units and hardware effects remain unproved. Return XOR retains original flag width,without arbitrary16-bit truncation. AUIPC/ADDI and file positions of19DE0/19DEC/19DFC/1AB34 are checked;16-byte window hashes identify source data without claiming actual extents or adding typed data owners.

Native code17880B+data674B:all18554B match officialID2966 bytes after original-address placement.109 C/H files,82 code units,166 comparisons/332 objects; all108 earlier sources and973 artifact records retained.999 direct transfers:927 measured targets/72 unresolved references. The two former literal-only providers are implemented.328 indirect transfers and387 potential returns do not prove complete CFG or execution.

Excluded trial: component-v1 audit mistakenly expected332B vectors; unchanged real vectors were328B,so the positive audit rejected it. The checker was corrected and component-v2 accepted. Failed trial retained; all previous code/data unchanged.

Potential tool: offline event/26-byte carrier comparison,showing fixed names and raw counters. Proposal only,no device behavior change. Next:888C/8B90 registration/input handlers and remaining providers/constant extents. No firmware/HOST/ISA execution,hardware or network. Entry0/PT_LOAD0 diagnostic ELF remains nonflashable. Historical privacy findings still hold publication; no commit/push.
