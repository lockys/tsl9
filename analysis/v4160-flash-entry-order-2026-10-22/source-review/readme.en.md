# Flash entry order and source ownership review

[繁體中文](readme.zh-TW.md)

This independent review checked the original six Flash functions, their known carrier references and the new readable C/C++ entry-order variant. It ran owned synthetic host tests and statically inspected actual compiled RV32 objects. No RV32 code, hardware, vendor service or firmware installer was executed.

## The original six bytes are live code

Original ID2966 V4.1.60 SHA-256 is `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`. The six complete functions occupy 262 bytes and 99 instructions. Bytes `18F50..18F55` are `758f98cb8280`: AND A4,A4,A3; SW A4,16(A5); RET RA. They complete the final fresh control-register read/mask/write and return. They are neither padding nor a free storage area, even though the preceding implementation happened to compile to 94 bytes.

The original program aligns A0 at 18EFA, after its first control read at 18EF6 and before its first control write at 18F00. The new 100-byte program aligns A0 at relative offset 6, after the read at +4 and before the write at +14. Original alignment was at +8. The new ordering repairs the memory-event ordering issue; it does not preserve the old alignment PC or every original instruction boundary.

## Actual source and incoming references

`source-inventory.json` records actual scans of both the original 8280-RELA carrier (`646dbe43…edb97`) and the earlier IRQ-integrated 8276-RELA carrier (`9a5bd413…179b9`). The four-relocation reduction belongs to that IRQ integration; 8276 is not the original carrier's count. All six Flash byte ranges, symbol roles and admitted references remain identical between these two carriers. Each scan inspects 24585 declared instruction boundaries.

Both inventories contain 23 incoming direct references and matching RELA records: 17 calls to function entries and six local loop branches. Eighteen named symbol roles comprise six public function symbols, six mapping symbols and six private loop labels. The private labels are 18EE0, 18F02, 18F0C, 18F1A, 18F2A and 18F44. Their admitted incoming branches are inside their own functions; this bounded inventory finds no external interior/tail reference. It does not exclude computed, loaded, resident/ROM or unknown external targets. One unresolved ROM relocation remains.

Eight known callers enter 9C0A at 9D00, 9E7A, 12E7A, 12F0C, 12F6E, 13078, 130FC and 1315E. The wrapper makes five helper calls. The separate 197BE resident callback wrapper contributes calls at 197C8, 197CE, 197D8 and 197DC. Only the previously admitted 9D00 continuation has the retained caller-liveness proof; a static incoming-reference inventory does not prove all caller argument, continuation or runtime behavior.

## Bounded new C changes and actual verification

`check-review.py` verifies the exact old-to-new source delta, not just a list of new hashes. The program now uses a dependent fixed-A0 identity/alignment primitive, two additional fixed-A4 base materializations and fixed-A5 masks for the first two polls. HOST fallbacks are the old pure AND expressions; the added host base operations return constants. The public header, host providers and canonical tests are byte-identical. The host launcher differs from the reviewed guarded launcher only by model path.

The immutable independent expected-effect fixture has SHA-256 `d2387b7983052b2b3b863223eaf3873e00435a1bd03b5833ba31a4c7ad569705`. It was freshly compiled against the new core in C11 and C++17. Each language passed 12 scenarios and 8964 assertions and rejected twelve actually compiled behavioral mutants. Every positive and negative executable was checked by the current host format guard before and after launch: 13 guarded executables per language. The alignment mutant targets the new HOST `FN_ALIGN0` macro; the other eleven control purposes remain the same. These are fresh variant results, rather than copied old counts. Canonical guarded host runs separately passed 5 groups/481 cases/247191 checks and six compiled controls per language.

Actual native C/C++ components are both 262 bytes/99 instructions, with 100 bytes/38 instructions for program and ELF SHA-256 `aeccc19da9c5764a386333dd26898429c35bf0ff40efb08c8f8417b11820339d`. `component-review.json` independently binds the actual old and new ELF bytes: five other function bodies are byte-identical to the prior component; program alone changes. A static decoder checks the early A0 order, live final six bytes, destination-register set and complete reachable CFG. Three actual native-byte controls are rejected. Original-tail checks separately reject three semantic mutations; the retained original-source proof also has twenty controls. These byte controls are static checks, not executed or compiled host mutants.

The new program's five loop targets retain original offsets 16/26/40/56/82; erase's 18EE0 loop is unchanged. An integration may validate and discharge/replace the old branch roles using this actual CFG. Merely preserving old numeric aliases without checking the corresponding new instructions is insufficient: old program offset 8 now falls inside a four-byte instruction. The initial scratch register is A2 instead of original A5, with further scratch allocation differences; physical fault/nonreturn GPR prefixes, complete instruction-boundary and asynchronous equivalence remain unproved. The wrapper's earlier save-order difference also remains.

## Replay and limits

```sh
python apk-analysis/tsl9-v4160-flash-entry-order-2026-10-22/source-review/check-review.py --project-root . --firmware /absolute/ID-2966-V4.1.60-decoded.bin
```

Published layouts use `analysis/v4160-flash-entry-order-2026-10-22/source-review/`. The default check reads current source hashes, exact source changes, retained receipts and original bytes. It does not claim a fresh artifact replay when build archives are absent. `--host-archive`, `--native-archive` and `--effects-archive` enable read-only replay of the corresponding retained archives. Historical Windows compiler/tool paths and executable formats must remain available and compatible. Build directories, executables and mutated source copies are excluded from the published seal.

The final native CLI forwards explicit `--firmware` to compilation and replay. The selected CLI-options receipt records an actual C compile using the same pinned image at another local path, successful replay with that explicit path, and rejection with the wrong default receipt context. This review forwards its own `--firmware` when a native archive replay is requested. Retained program bytes and their three static controls can also be rechecked without claiming that absent ELF artifacts were reread.

`inspect-source.py` can rerun the full reference inventory with explicit original image, original carrier, full layout, integrated carrier and its receipt paths, comparing `--reference source-inventory.json`. `inspect-component.py` can repeat the static old/new ELF audit with explicit component paths and `--reference component-review.json`. `run-effects.py` performs a fresh guarded host-only oracle build; use a new output directory. The historical unguarded runner is never invoked.

Source ownership, a naturally fitting component and host tests do not establish full-image symbol/layout integration, ROM implementation, installed BOOT identity, Flash persistence/timing/fault behavior, hardware compatibility or OTA acceptance. Parent integration work is a separate gate. This source review produces no new firmware BIN and implements no new product feature.
