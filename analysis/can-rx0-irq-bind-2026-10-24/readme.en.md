# CAN RX0 IRQ and ring integration

[繁體中文](README.md) · [Results](summary.json)

Three existing C/C++ units are composed:IRQ12C24(52B/17 instructions),receive-record18D78(164B/53 instructions),and ring12BC8(92B/32 instructions). All308B/102 instructions match after data-only original-address relocation encoding.

| Genuine partial link | Result |
| --- | --- |
| Code/data | 956B/335 original instructions plus456B data; prior648B code and all data unchanged |
| Regions/references | 116 nonzero architectural FUNC regions,2 explicit aliases,153 RELA and6 UND |
| Vectors | Slot36 binds the true12C24 entry;57 slots bind genuine code |
| Providers | Both direct18D78/12BC8 calls bind real definitions; conditional32B frame and both MRET paths retained |

Static call/data flow, without execution observation:

~~~mermaid
flowchart LR
  IRQ["Vector36 /12C24"] --> RX["18D78 /20B record"]
  RX --> ADAPTER["12C3C /ID, DLC, payload"]
  ADAPTER --> RING["12BC8 /32 slots x12B"]
  RING --> ROM["word4004C /unknown provider"]
~~~

The [SDK/layout comparison](hardware-sdk-match.json) matches original CAN1 address40006400,FIFO0 selection/release,mailbox fields and20B record layout to saved CH32V20x CAN_Receive. This is static register/algorithm correspondence,not physical chip attribution.

Only the saved header's CH32V20x_D8W branch defines BB63/LLE64;original vector entries point to1873E/8498,supporting a software-profile candidate. The [next LLE candidate](static-frontier.json) selects134B/64 instructions at8498–851E:128B frame,29 register save/load pairs,GP+384 indirect callback and MRET. The following two zero bytes remain separate data. This candidate is not yet reconstructed/compiled,and its IRQ/callback contracts remain unproved.

**This is not a flashable BIN.** The ring retains original12BD2 AUIPC;the VMA0 diagnostic component cannot establish original table address2000C038. Resident callback4004C,DLC<=8 and extended-ID/caller/filter policies remain unproved. Entries8448,8498,979E,19BD4,main9008,resident40000,and hardware/memory/IRQ/ROM/boot/OTA closure remain open.

Existing C/H and manifest are reused unchanged;current108 source comparisons/216 objects pass. Per-channel IRQ/queue-full diagnostics remain a candidate. Only offline record-layout reporting is added,no target logic changes.

[Three-original receipt index](publication-provenance.json) · [Experiment/replay](../../experiments/tsl9-can-rx0-irq-bind/readme.en.md). No target/HOST execution,ISA emulation,hardware/network operation or BIN generation occurred. Commit/push remain held for historical personal information.
