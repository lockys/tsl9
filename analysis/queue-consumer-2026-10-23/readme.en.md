# Queue consumer and feature entry points

[繁體中文](README.md) · [C/C++ candidate and measurements](../../experiments/tsl9-queue-consumer/README.md) · [107 original instruction rows](../irq-provider-2026-10-23/next-consumer.json)

The official V4.1.60 range `[0x12C58,0x12D92)` contains314B/107 instructions, SHA256 `89905d7666bbe8295d09c752f1fcd34246847ea86c6428b539406450f8980c0f`. These are static findings; neither the target nor hardware was executed.

| Evidence | Confirmed behavior | Unproved boundary |
| --- | --- | --- |
| `12C6E..12C8C` | PC-derived initial table`2000C038`, initial stride12; zero LHU skips the slot | S5/S6 preservation after opaque calls and actual ID0 reachability |
| `12C96..12CB0` | CSR800 clear, fresh indirect `[S3+76]` call, clear then-live S0 slot, CSR800 set, call82D2 | Resident identity, full preservation and global IRQ-lock semantics |
| `12CB4..12CEA` | After82D2 returns0: ID versus then-live S4, length4, bytes`B5 62`, opcode0 or`5A` | Specific seat or DND feature attribution |
| `12D0E..12D4A` | Calls820C/9454/9B36 and12ABE twice, with fresh byte/then-live S4 content | Callee behavior and all side effects |
| `12D4C..12D76` | `5A 55` path; after second resident call set frame byte26=`56`, byte31=0, then call12A08 | Physical reply transmission; A1/A2 retain resident residue |
| `12D78..12D90` | Fresh `[S7]`, then pointer+4 bit3; pass frame to14D2E only if81AA returns nonzero | Named gate flag and complete dispatch behavior |

The local CFG contains13 conditional branches,3 jumps,9 direct calls,2 indirect calls and one RET. Assuming opaque calls return, all107 nodes are syntactically reachable; this does not prove path feasibility. Cold blocks after RET remain part of the region. The candidate preserves the80B frame and then-live registers without changing the queue layout or protocol.

Useful potential additions:

- Offline queue diagnostics for the ID0/empty-slot representation conflict and slot-clear conditions. Prove reachability and synchronization before changing hardware counters or occupancy representation.
- Separate update/communication states for receipt, local dispatch, provider effects and observed features. A terminal character alone does not prove firmware execution.
- Version-aware checks: the fresh official81AA leaf loads`GP+167`; the older V4.1.00 model's`GP+175` must not be transplanted. This does not identify the physical chip.

Two short leaves now have separate C reconstructions: [GP status and bounded clear](../../src/native/receive/queue_small_providers.c). Their complete6B/18B object and diagnostic-linked functions match the official input in C11/C++17. These use diagnostic VMA0 and have not been composed with the consumer; all eight consumer UND symbols therefore remain. See the [provider experiment](../../experiments/tsl9-queue-small-providers/README.md).

The [formal summary](summary.json) binds receipts and source hashes. Public [C](receipts/queue-c.json)/[C++](receipts/queue-cpp.json) consumer receipts are original portable bytes. [Provider C](receipts/small-providers-c.json)/[C++](receipts/small-providers-cpp.json) and [curation](receipts/curated-source.json) receipts are path-only anonymized derivatives; their originals remain local and direct original-receipt replay is not claimed.

Next: the [188B filter](next-filter.en.md), remaining direct callees and dynamic resident/caller contracts. None of the suggested features has been added to hardware firmware. No flashable BIN was produced.
