# Curated sequence DATA pool and original-coordinate integration

[繁體中文](README.md)

The [178-byte C/C++ pool](../../src/native/receive/record_sequence_pool.c) is now curated in `src/`, with three genuine interior DATA labels checked through original-coordinate linking and HI/LO references. Verified byte coverage is **88.32%**, not feature completion or flash readiness.

| Item | Verified result |
|---|---|
| C/H files and units |151 files;121 code units plus4 independent DATA units |
| Original/curated C11/C++17 comparison |250 comparisons,500 objects;prior242 results and1453 artifact records unchanged |
| New DATA |One 178-byte owner plus3 zero-allocation interior labels;no new code |
| All DATA labels |One retained boot-data label plus3 new labels;all4 have actual positive-size storage backing |
| Original-coordinate byte equality |67,833/76,800 bytes=**88.32%**;code64,544B+data3,289B |
| Unresolved providers |27→24;two excluded direct entries plus22 literal DATA-address references |
| Flow and relocations |21,938 instructions,4,245 direct transfers,4,861 relocations;zero ordinary sequential-position gaps |

## Real storage and labels

Source labels `0x1A430`,`0x1A454`,`0x1A478` use offsets0/36/72 in one 178-byte readonly owner. Labels allocate no additional bytes and remain actual section-backed OBJECT symbols,not ABS substitutes or handler stubs. The original boot-data label at `0x1AB60` is retained.

The pool extent follows the [conservative selected-literal source/limit union](../record-sequence-pool-2026-10-25/readme.en.md). It is not an original declaration extent or a bound on arbitrary RAM values. Original bytes and relative source coordinates are retained;asynchronous execution and opaque ROM effects remain unproved.

## Non-loadable metadata

The native component retains a local compiler marker `$d.1` in non-ALLOC `.comment`. It has no relocation references or firmware-memory backing. Resection omits only this confirmed marker and additionally checks every remaining local/global symbol role. All actual CODE/DATA,interior labels and typed references remain verified.

[Summary](summary.json) · [Traceable evidence](evidence.json) · [Label contracts](provider-contracts.json) · [Next steps](next-providers.json)

Both languages yield the same diagnostic ELF:entry 0, no PT_LOAD segments. No new BIN,firmware/HOST-model/ISA/hardware execution or vendor requests. Complete MCU/ROM/RAM/IRQ/BLE OTA and private-ABI compatibility remain unproved.
