# Record-field transitions and notification paths

[繁體中文](README.md)

Reconstruct 19 original entries:3,682B/1,149 instructions and four bounded readonly windows totaling51B. Both C11 and C++17 preserve the original address encodings. Two separate short callback entries still tail to the unprovided body at `0xA476`.

- Complete source proof:146 C/H files,240 comparisons/480 objects;all prior236 results and1,417 artifact records retained.
- Joined component:56,958B code+2,647B data,4,086 relocations. Resolve17 prior providers,expose12 new dependencies,retain66 genuine undefined symbols.
- Original-coordinate placement:59,605/76,800B=77.61%,73 adjacent-only spans,no PT_LOAD,no executable entry,no ABS FUNC.
- `0xD14A` compares record offsets3/5/7/9,writes GP offsets232..235 only when changed,and tails to `0x13C4E`. Physical field meanings and notification effects remain unproved.
- AND15 at `0xC97E` and `0xCC20` bounds three16B lookup windows. The three-byte source at `0xD2CC` remains conditional on the installed ROM call contract. Three larger tables remain unprovided because their index ranges and possible interior references are not proved.

This is measured byte coverage,not feature completion. Installed ROM,private ABI,physical MCU/RAM/IRQ/BLE OTA and vehicle behavior remain unproved. No target/HOST-model/ISA/hardware execution,no backend access,no new BIN.

[Source](../../src/native/receive/record_field_transitions.c) · [Raw instruction evidence](evidence.json) · [Field and range contracts](provider-contracts.json) · [Summary](summary.json) · [Next providers](next-providers.json) · [Proposed features](feature-candidates.json)

Replay requires the pinned LLVM tool directory and locally produced measurement receipts;set `LLVM_BIN` to that directory:

```sh
python3 experiments/tsl9-record-field-transitions/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-field-transitions/build/native-v1
python3 experiments/tsl9-original-layout/build-v52.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/record-field-transitions-v1
python3 experiments/tsl9-original-layout/verify-flow-v52.py --replay experiments/tsl9-original-layout/build/record-field-transitions-flow-v1
```
