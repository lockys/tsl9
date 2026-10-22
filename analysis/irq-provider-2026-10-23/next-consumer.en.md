# Next: queue consumption and dispatch

[繁體中文](next-consumer.md) · [Instruction evidence](next-consumer.json)

`[0x12C58,0x12D92)` covers314B/107instructions, SHA256 `89905d7666bbe8295d09c752f1fcd34246847ea86c6428b539406450f8980c0f`, without a readable C reconstruction. Do not stop at the RET at`0x12D0C`; locally reachable cold blocks follow it.

Preserve the80B frame and S0..S7/RA, fresh slot reads/clearing, CSR`0x800` clear/set, then-live physical registers across opaque providers, and later dispatch/direct/indirect call boundaries. CSR operations are not yet a proved global IRQ lock, and resident pointers are not assumed standard memcpy.

ID0 is both an empty-slot sentinel and a consumer skip condition. This representation conflict is a possible offline-diagnostic lead; actual ID0 reachability, synchronization/resident effects and hardware packet loss remain unknown. Reconstruct original behavior before considering explicit occupancy/counters. No layout, protocol or hardware behavior changed. Complete callers, IRQ, memory and silicon remain unproved; no target/ISA/MMIO execution occurred.
