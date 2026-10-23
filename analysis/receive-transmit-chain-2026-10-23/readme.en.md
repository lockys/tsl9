# Original-PC receive, dispatch and transmit chain

[繁體中文](README.md) · [English](readme.en.md)

Freshly linked selected C/C++ sources provide a **1588B/555-instruction/97-function** subcomponent. All bytes across nine original-PC code spans match V4.1.60. Source remains in `src/native/receive/`; the [recipe](../../experiments/tsl9-receive-transmit-chain/README.md) uses genuine providers and no opcode carrier.

Spans:81AA/6B,820C/60B,82D2/188B,8520/168B,8A56/280B,12A08/102B,16896/326B,16B7C/246B,18CA4/212B.

A separate full **1902B/662-instruction** partial link preserves the queue consumer,107FUNC/97RELA and four UND providers:9454,9B36,12ABE,14D2E. Their five callsites are12D16/12D1C/12D2C/12D46/12D8C. The full reconstruction remains incomplete.

The [runtime boundary ledger](runtime-boundaries.json) retains six unknown transfers:8356,8A8E,8AB4,12A4E,16BF8 and the no-link tail8B50. The filter reads then-live S9; its initial40000 cannot be frozen across opaque calls. Resident identity, GP/stack state, IRQ/MMIO/fault behavior remain unknown. RX LOAD68558B includes66970B of unproved gaps; no flashable BIN was produced.

[C](evidence/native-c.json) and [C++](evidence/native-cpp.json) receipts each pass1538 controls and check all1217 complete LLVM address/byte rows. Input groups retain139 direct inputs,145 tagged-chain inputs,83 peripheral inputs,five upstream receipts and three current proof files. Groups overlap and are not summed as unique files. [Independent review](independent-review.json) rejects24/24 mutations.

Failedv1 is retained: two real small functions had names differing from earlier composition; v2 uses two explicit C name mappings, without ABS placeholders. The earlier proof's structural checks accepted extra/expanded RX LOADs and omitted transitive provenance; verify-v2 checks the complete PHDR vector and upstream closure over unchanged compiler artifacts. Older receipts are preserved.

[Proposed offline diagnostics](feature-opportunities.json) could distinguish several tagged return4 paths and report SPI timeout-zero versus received-zero ambiguity. Missing observations must remain unclassified. This feature is proposed, not implemented.

[Publication provenance](publication-provenance.json) retains four portable original JSON files byte-for-byte. Raw compiler logs with personal paths remain local. No vendor API, HOST/ISA model or hardware operation occurred; GitHub publication follows prior authorization.
