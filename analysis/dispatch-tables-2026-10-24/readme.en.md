# Channel routing, feature dispatch and relative tables

[繁體中文](README.md)

Bound 12ABE and 14D2E using **2,736B / 956 instructions / 269 regions** from eight existing C/C++ units, plus **60B / 15 entries** in two signed-relative tables. Both C11 and C++17 reproduce the original code and table bytes after static original-VA encoding. Every table target has a genuine code body.

The main component contains **9,836B code + 516B data**, 783 nonzero FUNC regions, 26 genuine entry aliases, 698 RELA and 82 UND. C/C++ bytes match. All previous 7,100B code, 456B data and 62 selected nonzero vector bindings remain. Expanding the dispatchers exposes 69 external symbols; one is bound to the existing C6A8 decoder, leaving 82 unresolved symbols. This does not establish that all feature implementations are complete.

| Checked scope | Evidence and limits |
| --- | --- |
| Channel routing | Built-in and SPI routes, filter inputs and program paths retained; physical CAN/SPI outcomes unproved |
| 14D2E body | Original 16-byte frame, mode guard, record-ID comparisons and tails retained; no seat or DND attribution |
| Relative tables | 28B at original1A6B8 and 32B at1A6D4; 15 ADD32/SUB32 pairs and two HI20/LO12 pairs have correct owners; [details](relative-tables.json) |
| Clock deduplication | Parent supplies the exact 26B; [C selection](../../experiments/tsl9-dispatch-tables/derive-selection-v1.py) omits only those three definitions and preserves retained bodies/references |

The 95 curated C/H files and manifest are unchanged. Source-copy curation remains 138 comparisons / 276 objects, with two additional C-selection compiler objects this round. Source-copy equality does not prove every curated unit matches firmware. The selected code and table ranges receive independent original-byte audits.

Use the replay commands in the [experiment](../../experiments/tsl9-dispatch-tables/readme.en.md). [Summary](summary.json), [remaining symbols and candidates](next-providers.json), [publication provenance](publication-provenance.json).

Possible features include an offline mode/record-ID-to-handler viewer and passive dispatch diagnostics; these are not implemented. **This unresolved VMA-zero ET_REL is not a flashable BIN.** Physical hardware, installed ROM/ABI, actual code/table/RAM placement, full IRQ and BLE OTA compatibility remain unproved. No target, HOST-model or ISA execution, hardware/network access, commit or push occurred. Historical privacy findings remain.
