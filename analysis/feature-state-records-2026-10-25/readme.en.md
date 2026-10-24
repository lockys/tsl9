# Feature state and records: offline reconstruction

This milestone adds 19 selected function bodies and reuses existing predecessor providers. C11/C++17 original-instruction comparison covers 1,260 bytes, 424 instructions, 83 direct transfers and 16 code/data address pairs. Explicit architecture ports retain original registers and private calls.

| Range / entry | Confirmed static behavior |
|---|---|
| `1056E..1061C` | Five predicates for byte/halfword zero fields, byte-three types 9/10 or four, byte-four limit 14 and byte-five masks/allowed values. Preserve access widths and branch order. |
| `106C0` / `106E0` | Use the signed value at byte eight through the GP+84 pointer to gate passing a selector to unprovided `EBAC`; the shared entry selects 82. |
| `107C6` | Call a predicate through private A3/A4 arguments. On true, increment/truncate a byte counter and dispatch existing state handling when the unsigned limit is reached; otherwise retain the count. On false, clear it. No invented bounds. |
| `10870` / `10AC6` / `10B0A` | Produce selectors 82..87 from distinct byte/bit priority orders; retain priority,shared handling and original scheduling parameters. |
| `108D8` / `10936` / `10944` / `109C4` / `10A00` | Predicate/state-gated record changes: type,nibble counter/lookup,two big-endian halfwords each plus 200,byte plus 25 or fixed byte values,followed by an existing output call. |
| `10A16` | Increment a byte field and execute original signed REM 15. Select among three unprovided tables by mode/halfword state; retain each branch's fixed values and zero stores separately. |
| `10B60` | Dispatch by record halfword ID to a predicate,GP counter byte,unsigned limit and mode; one ID performs two ordered operations. |
| `10C1E..10C36` | Set nominal A0,A1=0,A2=20 and tail-transfer through ROM slot 72. Preserve the following original RET without claiming it is a confirmed separate function. |

New unprovided dependencies are function `EBAC` and data addresses `1A4E4`,`1A518`,`1A528`,`1A538`. Their lookup payloads have not been extracted, interpreted or supplied; no synthetic table was substituted. Record transformations are therefore not independently operational.

Evidence: [original instructions](evidence.json), [reconstructed C](../../src/native/receive/feature_state_records.c), [compiler and comparison](../../experiments/tsl9-feature-state-records/build-v1.py). [繁體中文](README.md)

Whole-source proof passes 216 comparisons/432 objects. Eleven imports are resolved and five dependencies exposed; 126 remain. All 45,345 selected original-coordinate bytes match. Static flow covers 2,489 direct transfers with no ordinary continuation gaps. No unprovided callback-address reference remains in this selected component; indirect runtime targets remain unproved. Time units,feature attribution,private ABI and hardware/OTA remain unproved; no target or hardware execution and no new BIN.
