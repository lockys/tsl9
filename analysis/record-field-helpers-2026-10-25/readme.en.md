# Record helpers and callback bodies

[繁體中文](README.md)

Add12 complete original entries:1,564B/539 instructions,163 private code regions,129 direct transfers and nine typed address references. Keep CD4E/CD58 and F414/F468 as separate entries.

- Both C11 and C++17 pass original encoding comparisons.147 C/H files,242 source comparisons/484 objects;all prior238 results and1,429 artifact records retained.
- Resolve10 prior providers,expose two unprovided static data addresses,retain58 genuine undefined symbols. Preserve all16 parent readonly sections.
- Component58,522B code+2,647B data/4,233 relocations. Original-address placement matches61,169/76,800B=79.65% in63 adjacent-only spans. The diagnostic ELF has no PT_LOAD or executable entry.
- CD58 stores arguments into state offsets7/8;physical meanings remain unknown. F468 is a real callback body;registration paths contain raw5000 with unproved timing units.
-12AD0 retains a128B stack frame and94/106 length arguments. Static source contents and complete called-function semantics remain unprovided.

Measured byte coverage is not feature completion. Installed ROM,private ABI,physical MCU/RAM/IRQ/OTA and vehicle behavior remain unproved. No target/HOST-model/ISA execution,no hardware/backend access,no new BIN.

[Source](../../src/native/receive/record_field_helpers.c) · [Raw instructions](evidence.json) · [Contracts](provider-contracts.json) · [Summary](summary.json) · [Next providers](next-providers.json) · [Proposed features](feature-candidates.json)

Replay requires the pinned LLVM tools and locally produced receipts;set `LLVM_BIN` to the tool directory:

```sh
python3 experiments/tsl9-record-field-helpers/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-field-helpers/build/native-v1
python3 experiments/tsl9-original-layout/build-v53.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/record-field-helpers-v1
python3 experiments/tsl9-original-layout/verify-flow-v53.py --replay experiments/tsl9-original-layout/build/record-field-helpers-flow-v1
```
