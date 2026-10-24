# Original LLE IRQ wrapper in C/C++

[繁體中文](README.md) · [Results](summary.json) · [Source](../../src/native/irq/lle_irq.c)

All134B/64 instructions at8498–851E are reconstructed and byte-identical in C11/C++17. Three architectural regions are60B entry,10B callback and64B exit. The128B frame,29 save/load pairs,fresh GP+384 callback,full-width JALR and MRET remain. Original GP is not saved. The two zero bytes at851E–8520 remain separate data,not compiled code.

| Genuine partial link | Result |
| --- | --- |
| Code/data | 1090B/399 original instructions plus456B data;prior956B code and all data unchanged |
| Regions/references | 119 nonzero architectural FUNC regions,3 explicit aliases,153 RELA and5 UND |
| Vectors | Slot64 binds the genuine60B entry with all134B present;58 slots bind real code |
| Source verification | 81 C/H files,54 code units plus1 independent data unit;110 comparisons/220 objects |

The fresh function-source verifier passes108 comparisons/216 objects,preserving all prior106 results and637 artifact records. Independent pointer data adds2 comparisons/4 objects. This uses pinned Windows LLVM;cross-machine replay is not established.

The [callback-origin evidence](callback-origin.json) observes a valid prefix from199E2 loading literal address20000008 and storing into then-live GP+384. One raw direct GP+384 SW encoding is found;complete alias/initializer-uniqueness analysis is not claimed. The8EA8 JAL is an encoded-call candidate without established containing-function or startup reachability.

~~~mermaid
flowchart LR
  RAM["word20000008 /value unknown"] --> INIT["199E2 prefix /pointer copy"]
  INIT --> GP["then-live GP+384"]
  GP --> IRQ["8498 LLE wrapper"]
  IRQ --> CB["full-width JALR /provider unknown"]
~~~

Saved SDK CH32V20x_D8W vector64 corresponds to this software-profile candidate,not physical chip identification. Actual callback value/ABI,GP/SP preservation,IRQ nesting/fault behavior and startup reachability remain unproved.

The VMA0 ET_REL places the wrapper at diagnostic offset956,**not original8498 execution placement or a flashable BIN**. Entries8448,979E,19BD4,main9008,resident40000,and hardware/memory/ROM/final-layout/boot/BLE OTA remain open. No target/HOST execution,ISA emulation or hardware/network operation occurs.

The next [ECALL restore candidate](ecall-candidate.json) is78B/35 instructions at8448–8496,followed by two zero bytes. It applies CSRS0x804 mask32,loads mepc from SP+0,and restores a register frame. Special-CSR meaning and trap context remain unproved. The earlier80B [bounded probe](ecall-frontier.json) is retained without claiming80B of confirmed code.

BLE startup/callback diagnostics remain a feature candidate;only offline origin reporting is added. The [provenance index](publication-provenance.json) preserves4 portable original receipts byte-for-byte;the large curation original remains local. See [experiment/replay](../../experiments/tsl9-lle-irq/readme.en.md). Commit/push remain held for historical personal information.
