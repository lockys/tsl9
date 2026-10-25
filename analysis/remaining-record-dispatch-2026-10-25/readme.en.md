# Remaining record dispatch and support entries

[繁體中文](README.md)

Add38 complete entry intervals:6,022B/1,926 instructions,568 private code regions,462 direct transfers and19 typed address references. Includes large B730/BD88 dispatch bodies and their callback/support closure.

- C11/C++17 original encodings match.148 C/H files,244 source comparisons/488 objects;all prior240 results and1,441 artifact records retained.
- Independent parsers agree on all fields/bytes of1,043 actual ELF sections,1,214 symbols and500 relocations. Retain the old parser;only the new section ceiling and explanatory doc differ.
- The first trial compressed two RAM-address ADDIs. Retaining their original32-bit widths passes native-v2;the failed native-v1 remains preserved.
- Resolve29 prior providers,expose five data references,retain34 undefined symbols:32 data addresses and excluded14056/40000 entries. Unknown indirect ROM implementations are outside that compiler-symbol count.
- Component64,544B code+2,647B data/4,733 relocations. Original-address placement matches67,191/76,800B=87.49% in40 adjacent-only spans. No PT_LOAD or executable entry.

19BF0..19CA6 is an already reconstructed software memory-transfer routine. Its first12B block is not the whole function or a ROM wrapper. Source extents and actual hardware memory remain to be proved.

Measured byte coverage is not feature completion. Private ABI,installed MCU/ROM/RAM/IRQ/OTA and vehicle behavior remain unproved. No target/HOST-model/ISA/hardware execution,no backend access,no new BIN.

[Source](../../src/native/receive/remaining_record_dispatch.c) · [Raw instructions](evidence.json) · [Contracts](provider-contracts.json) · [Summary](summary.json) · [Next providers](next-providers.json) · [Proposed features](feature-candidates.json)

Replay requires pinned LLVM tools and locally produced receipts;set `LLVM_BIN` to the tool directory:

```sh
python3 experiments/tsl9-remaining-record-dispatch/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-remaining-record-dispatch/build/native-v2
python3 experiments/tsl9-original-layout/build-v54.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/remaining-record-dispatch-v1
python3 experiments/tsl9-original-layout/verify-flow-v54.py --replay experiments/tsl9-original-layout/build/remaining-record-dispatch-flow-v1
```
