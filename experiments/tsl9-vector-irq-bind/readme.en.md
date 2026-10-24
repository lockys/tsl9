# Native linking of the existing C/C++ IRQ provider

[繁體中文](README.md) · [Analysis](../../analysis/vector-irq-bind-2026-10-24/readme.en.md)

[integrate-v1.py](integrate-v1.py) replays current source and parent-component evidence, then reads genuine retained C11/C++17 products of [irq_flag.c](../../src/native/irq/irq_flag.c). All76B must equal original16FB6–17002, with exact allocation/symbol checks and no external dependency.

[joined-v1.ld](joined-v1.ld) binds a real provider and section-relative alias in an unresolved diagnostic component. [contract-v1.json](contract-v1.json) pins sources, tools, original code and parent products. All144 references, data and prior code prefixes are checked; only the genuine16FB6 binding changes.

With the pinned toolchain and complete retained local products, replay read-only:

~~~sh
python3 experiments/tsl9-vector-irq-bind/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-vector-irq-bind/build/component-v1
~~~

Set LLVM_BIN locally; Windows may use its installed python. Fresh builds require a new output folder. Public receipts cannot replace missing objects or establish cross-machine replay.

No C/H file, manifest or new handler compilation is added. The current80-file inventory,53 code units plus1 independent data unit, and108 comparisons/216 objects are still checked through the parent proof. This traceable native partial link does not establish physical execution, IRQ ABI or flashing compatibility.
