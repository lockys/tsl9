# Output dependencies and delayed flags

[繁體中文](README.md)

Ten complete functions were added: 374B/130 instructions, with identical C11/C++17 objects. Six previous imports now have genuine bodies with no new dependencies; 173 providers remain, down from 179. Native address placement matches all 34,548B of selected code/data to the official BIN. **The result is still an entry=0, PT_LOAD=0 diagnostic ELF, not flashable firmware.**

| Original entries | Confirmed static behavior |
| --- | --- |
| `8E6A`, `F84A` | Original tuples and tail transfers through ROM slots `0x40058`/`0x40048` |
| `9F7A`, `9FC8` | Clear flag, conditionally schedule, reload configuration/flag in callback |
| `D7D4`, `D810` | Record field updates, two calls on the same pointer, state dispatch/clear |
| `F818`, `F822`, `F82C`, `F838` | Four RAM byte store/read/copy entries |

`9FC8` schedules the numeric value 10000; its time unit is unknown. `9F7A` retains `(flag XOR 1) & 1`, which is not general boolean inversion. Callback reads must not be replaced with scheduling-time snapshots.

`D7D4` retains a signed byte load and OR, then passes the same stack record pointer to `12A08` twice. Payload equality between calls is unproved because the first call may modify memory. `D810` preserves the original 1–19/24/25/26 dispatch and subsequent clear order. Product labels remain unknown.

See [raw instructions](evidence.json), [83 semantic witnesses](provider-contracts.json), [results/receipt identities](summary.json), [remaining dependencies](next-providers.json) and [read-only diagnostic candidates](feature-candidates.json). Proposed diagnostics explain delayed flag updates and record submission provenance; no hardware feature was added.

All 124 C/H files passed 196 comparisons/392 objects; the previous 123 files are unchanged. Static flow covers 11,478 instructions and 1,922 direct transfers with no ordinary continuation gaps. Of those targets, 1,709 have measured implementations and 213 remain references only. Runtime indirect targets, IRQ returns, the EBREAK/vector boundary and reachability remain unproved.

Read-only checks from the repository root:

```sh
python scripts/verify-curated-source.py
python experiments/tsl9-output-dependencies/derive-v1.py --counts
```

`spec-v1.json` pins measured tools/headers. With a matching existing `LLVM_BIN`, use `build-v1.py --tool-dir "$LLVM_BIN" --trial <new-name>` for a new native trial; full integration replay also needs locally generated historical receipts. No target, HOST model, ISA emulator, hardware operation or new BIN was executed/added. Physical chip, ROM/RAM/IRQ, startup and original OTA compatibility remain unproved.
