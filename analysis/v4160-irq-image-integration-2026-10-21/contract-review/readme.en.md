# Independent full source-image contract review

[繁體中文](readme.zh-TW.md)

The final source-integrated-99841... C and C++ artifacts pass independent readback. Both 76800-byte images have SHA-256 47f200dce24be25ac89d57922689da536259935e8615ba8195b10ca192895e1c and differ from the original at exactly eight bytes, 0x9A44..0x9A4C: a permutation of four complete two-byte stack stores. This is an offline artifact/static-contract result, not flash validation.

## Actual independent checks

The partial object has exactly 691 allocation names with original type, flags, size, alignment, entry size and relative VA. All 686 retained storage sections match, with 35160-byte RAM remaining NOBITS. All 8270 outside-owned RELA occurrences match as a multiset of owner/site/type/full symbol role/signed addend, including eight incoming references. Six native main JALs use the original offsets; helpers have no RELA. Four old private branch relocations are discharged, yielding 8276 total.

Every original global/weak role remains, with exactly five additional public C FUNC names. All53 canonical bindings are real section-relative NOTYPE/size0 records. ROM remains the sole partial-object UND. The linked ELF keeps all691 original placements and entry0x8000; LOAD VMA equals physical/LMA. The690 file-backed source sections cover all76800 bytes, matching LOAD contents and image bytes exactly. No padding, RAM export, ROM bytes or original-byte fallback is credited.

Seventeen actual in-memory raw ELF/image mutations per language are rejected: ABS alias, wrong size, changed/missing RELA, hidden allocation, RAM converted to PROGBITS, wrong VA/LMA/ELF entry, truncation/append and image changes both outside and inside the allowed range. The latter checks exact admitted byte values. These are static raw controls, not compiled source mutants or target execution.

## Provenance and limited metadata exceptions

source-provenance.json independently binds final runnerb26410ae9a0d9dece3e5404fb311407dd7c3022a08a7d2fb8c8df7834496c854, the portable manifest and two actual receipts. Each mode has144 artifacts/logs read back,44 actual commands,36 dependency rules,71 pinned native sources/headers and four controlled generated inputs. The two filtered carriers remove only the five bounded assembly blocks; adapters contain only declarations, original section attributes and true same-TU aliases. The53-label script is checked for all691 sections/KEEP/assertions and exact assignment grammar. All object inputs and outputs are inside the fresh build folder; the historical carrier is not an input to the new link.

Metadata admission is exact: five selected $d-to-$x mappings; two added typed FILE records; two extra .comment mappings and two attributes-origin local ABS $d records, all unreferenced. In actual main.o, $d.2 belongs to nonallocated .riscv.attributes; helpers.o has $d.5 there. Partial linking converts those markers to ABS0; the .comment markers remain section-relative. They supply no provider/storage. Other old local/SECTION roles remain, and four old private helper branch labels are discharged only with their sole old branch RELA.

The review detected a runner hash change from ff18322a... after a relative replay-path correction and withheld provenance closure. C/C++ were then genuinely rebuilt under1929598f..., rather than rebinding old receipts. Selected final evidence is final-c.json, final-cpp.json and source-provenance.json. The preliminary-c.json/review-c.json/review-cpp.json files are historical early results only.

## Replay and limits

From the project root, the Python CLI reads artifacts without compiling or generating an image:

~~~sh
python -B apk-analysis/tsl9-v4160-irq-image-integration-2026-10-21/contract-review/review.py --merged /path/source-integrated.o --linked /path/ADDRESS-WITNESS-ONLY.elf --image /path/NOT-FLASH-VALIDATED-irq-callframe.bin --label c --output /path/this-review/replayed-c.json
python -B apk-analysis/tsl9-v4160-irq-image-integration-2026-10-21/contract-review/provenance.py
~~~

The checker requires the pinned historical baseline ELF, original BIN, plan and parser available in this case's checkout; missing inputs fail. Recorded platform paths do not establish a build on another machine. MMD excludes system headers, so this is not a separately reproduced entire toolchain environment.

The actual strict link rejects the missing resident ROM; ROM=0x40000 in the numeric witness is not an implementation. The changed prologue save order leaves transient stack/asynchronous IRQ equivalence unproved. Hardware, BLE, CAN, flashing, OTA and target execution remain unverified. This reviewer neither compiled nor generated a BIN and did not edit original sources or old seals.

