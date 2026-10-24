# Control gates, modes and callbacks

[繁體中文](README.md)

Twelve complete functions were reconstructed: 892B/308 instructions, with identical C11/C++17 objects. Five previous imports now have genuine bodies with no new dependencies; 168 providers remain, down from 173. Native address placement matches every selected byte across 35,440B of code/data to the official BIN. **The result remains an entry=0, PT_LOAD=0 diagnostic ELF, not flashable firmware.**

| Original entries | Confirmed static behavior |
| --- | --- |
| `81EE`, `A658`, `A9DE` | Read condition bytes and set a pending byte |
| `CD6A` | `0x65E` bitmap dispatch, full-width gates and follow-up calls |
| `D07C`, `D0EE` | Condition gate, three word constants and a ROM-slot tuple |
| `FD6A`, `FDF6`, `10022` | Mode toggle, full-width zero tests and ordered byte stores |
| `FB1E`, `FB5E`, `FE6A` | Self scheduling/cross cancellation, modes and elapsed-counter tests |

`FD6A` toggles only for the full input value 3. `D07C` does not truncate its input before comparison. `FE6A` reloads configuration and stored counter values after opaque calls, preserving `uint32(fresh-stored)>1499`. The time unit of scheduling value 1500 is unknown. Both callbacks and cancellation order are retained without assigning guessed product labels.

See [raw instructions](evidence.json), [135 semantic witnesses](provider-contracts.json), [results/receipt identities](summary.json), [remaining dependencies](next-providers.json) and [read-only diagnostic candidates](feature-candidates.json). Proposed diagnostics explain dispatch/skip reasons, mode/counter state and callback relationships. Only static reports exist; no hardware feature was added.

All 125 C/H files passed 198 comparisons/396 objects; the previous 124 files are unchanged. Static flow covers 11,786 instructions and 2,021 direct transfers with no ordinary continuation gaps. Of those targets, 1,824 have measured implementations and 197 remain references only. Runtime indirect targets, IRQ returns, the EBREAK/vector boundary and reachability remain unproved.

Read-only checks from the repository root:

```sh
python scripts/verify-curated-source.py
python experiments/tsl9-control-gates/derive-v1.py --counts
```

`spec-v1.json` pins measured tools/headers. With a matching existing `LLVM_BIN`, use `build-v1.py --tool-dir "$LLVM_BIN" --trial <new-name>` for a new native trial; full integration replay also requires locally generated historical receipts. No target, HOST model, ISA emulator, hardware operation or new BIN was executed/added. Physical chip, startup/ROM/RAM/IRQ and original OTA compatibility remain unproved.
