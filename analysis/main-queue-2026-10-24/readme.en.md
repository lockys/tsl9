# Main-loop queue and receive paths

[繁體中文](README.md)

Bound the 12C58 queue consumer and 17002 flag consumer with necessary receive dependencies. Ten existing C/C++ units supply **1,464B / 509 instructions / 59 regions**. Both C11 and C++17 reproduce the original bytes after static original-VA encoding, including 68 added typed references.

The main component contains **7,100B code + 456B data**, 514 nonzero FUNC regions, 25 genuine entry aliases, 424 RELA and 16 UND. C/C++ component bytes match. All previous 5,636B code, 456B data and 62 selected nonzero vector bindings remain unchanged. Two main entries are resolved while 12ABE and 14D2E are newly exposed, leaving the UND count at 16.

The complete [record_program.c](../../src/native/receive/record_program.c) remains in src. A [reproducible C selection](../../experiments/tsl9-main-queue/derive-selection-v1.py) removes only the disarm definition already supplied by the parent's verified 34-byte body. All retained compiler bodies and typed references match the complete source. The 95 curated C/H files and manifest are unchanged: curation totals 138 comparisons / 276 objects, with two additional selection compiler objects.

The original [AUIPC/ADDI evidence](queue-layout.json) yields 2000C038 at the original PC. The 12-byte argument and index comparison against 32 describe a nominal 384-byte range. Actual placement, RAM initialization, resident register preservation and runtime loop bounds remain unproved.

The whole clock-fields object at 1973C and the irq source object containing 9A42 did not pass this round's original-byte audit and were not bound. Source-copy equality does not prove all curated sources match firmware. [Next providers](next-providers.json) records the errors, missing extent evidence and the 28-byte table in 14D2E's unit.

Use the replay commands in the [experiment](../../experiments/tsl9-main-queue/readme.en.md). [Summary](summary.json), [pending providers](pending-providers.json), [publication provenance](publication-provenance.json).

Possible features include passive queue occupancy and drop-reason diagnostics; these are not implemented. **This unresolved VMA-zero ET_REL is not a flashable BIN.** Hardware, installed ROM/ABI, full memory/IRQ and BLE OTA compatibility remain unproved. No target, HOST-model or ISA execution, hardware or network access, commit or push occurred. Historical privacy findings remain.
