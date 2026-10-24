# Linking retained CAN RX0 C/C++ units

[繁體中文](README.md) · [Analysis](../../analysis/can-rx0-irq-bind-2026-10-24/readme.en.md)

Sources are [ring_irq_adapter.c](../../src/native/irq/ring_irq_adapter.c),[irq_provider.c](../../src/native/receive/irq_provider.c),and [ring_insert.c](../../src/native/receive/ring_insert.c),unchanged with their manifest.

[integrate-v1.py](integrate-v1.py) replays current source/parent evidence and inspects three genuine C11/C++17 objects,16 regions and9 original control relocations. Original opcode/register/condition bits and destinations must match;data-only original-address encoding must recover all308B. [contract-v1.json](contract-v1.json) pins objects,sources,tools,original bytes and spans.

[joined-v1.ld](joined-v1.ld) retains within-span original fall-through/cold ordering,then binds vector36 to the true12C24 entry. The alias is a zero-size section label;the actual entry region is14B within a complete52B adapter,not an empty handler.

With pinned tools and complete retained local products,replay read-only:

~~~sh
python3 experiments/tsl9-can-rx0-irq-bind/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-can-rx0-irq-bind/build/component-v1
~~~

Set LLVM_BIN locally;Windows may use its installed python. Fresh builds require a new output folder. Public receipts cannot replace missing objects or establish cross-machine replay.

Only partial linking is added. Current80 files,53 code units plus1 data unit,and108 comparisons/216 objects are verified through the whole parent evidence. All153 typed references and local/global owner/value roles are checked;this does not prove every RAM pointer or IRQ/resident ABI.

Original12BD2 AUIPC and indirect callback4004C remain intact. Final original placement,RAM/ROM/IRQ and BLE OTA remain unproved. No firmware execution or flashable BIN generation occurs.
