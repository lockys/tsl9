# Output builder and comparison functions

[繁體中文](README.md)

Six complete original functions were reconstructed: 956B/298 instructions, with identical C11/C++17 objects. The integrated native linker places 34,174B of measured code/data at original addresses; every selected byte matches the official BIN. There are still 179 unimplemented providers. The diagnostic ELF has entry=0 and PT_LOAD=0: **it is not flashable firmware**.

| Original range | Confirmed static behavior |
| --- | --- |
| `9AE4–9AF0` | Store 32-bit value 2 at `0x40010814`; physical pin unknown |
| `B6F4–B730` | Byte gate followed by full 32-bit comparisons and calls |
| `DEA0–DEE2` | State gate, byte store, follow-up calls and tail transfers |
| `17C4E–17CB2` | Assemble a `0x04F3` record and call `12A08` |
| `17CB2–17CF4` | Preserve unsigned difference/direction logic and flag/mask updates |
| `17CF4–17F80` | Two records, eight comparisons, 16-bit countdown and callback cancellation |

Four record bytes receive no assignment in this function. Reads of old stack bytes before later writes are also preserved. The comparator tests `uint32(A5-A6+5)<=10`; the countdown decrements and truncates to 16 bits without a prior zero guard. Product labels, timing units, concurrency, private ABI and physical behavior remain unproved.

See [raw instructions](evidence.json), [101 semantic witnesses/eight tuples](provider-contracts.json), [results and receipt identities](summary.json), [remaining dependencies](next-providers.json) and [read-only diagnostic candidates](feature-candidates.json). Four previous imports now have genuine bodies; `9FC8` and `D810` are newly exposed dependencies. They and the heavily referenced `8E6A` are next.

All 123 C/H files passed 194 comparisons/388 objects; the previous 122 source files are unchanged. Static flow covers 11,348 instructions and 1,899 direct transfers with no ordinary continuation gaps. Runtime indirect targets, interrupt returns and the EBREAK/vector boundary remain unproved.

Read-only checks from the repository root:

```sh
python scripts/verify-curated-source.py
python experiments/tsl9-output-builder/derive-v1.py --counts
```

`spec-v1.json` pins the measured tools and compiler header. With an existing `LLVM_BIN`, use `build-v1.py --tool-dir "$LLVM_BIN" --trial <new-name>` for a new native trial. Complete integration replay additionally requires the locally generated historical receipts. No firmware, HOST model, ISA emulator or hardware was run; no BIN was added. Physical chip, startup/ROM/RAM/IRQ and OTA compatibility remain unproved.
