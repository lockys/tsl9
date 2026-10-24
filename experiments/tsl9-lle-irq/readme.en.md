# LLE IRQ native compilation and linking

[繁體中文](README.md) · [Analysis](../../analysis/lle-irq-2026-10-24/readme.en.md)

[lle_irq.v1.c](src/lle_irq.v1.c) is copied unchanged into [src/native/irq/lle_irq.c](../../src/native/irq/lle_irq.c). C expresses live-GP addressing and the volatile callback load;explicit architecture ports retain the original frame/register/JALR/MRET. An ordinary C IRQ ABI is not claimed.

[build-v1.py](build-v1.py) uses the pinned Windows LLVM recipes in [spec-v1.json](spec-v1.json) to compile C11/C++17 and inspect134B/64 instructions,three60/10/64B definitions,zero UND/RELA and all allocated bytes. Two trailing zero bytes are excluded from code.

[integrate-v1.py](integrate-v1.py) uses [joined-v1.ld](joined-v1.ld) to extend the genuine parent. All153 typed references and local/global owner/value roles are checked. The vector64 zero-size alias owns a genuine60B entry within the complete134B wrapper.

With pinned tools and complete retained local products,replay read-only:

~~~sh
python3 experiments/tsl9-lle-irq/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-lle-irq/build/trial-v1
python3 experiments/tsl9-lle-irq/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-lle-irq/build/component-v1
~~~

Set LLVM_BIN locally;Windows may use its installed python. Fresh builds require new output folders. Public receipts cannot replace missing objects or establish cross-machine replay.

The [parent derivation](parent-manifest-v1.py) restores exact80-file bytes;only one source/unit is added. [integration-v1.json](integration-v1.json) pins actual sources,tools and receipts. Fresh curation passes108 comparisons/216 objects plus independent pointer data2/4,total110/220. All prior106 results and637 artifact records are unchanged. The old parent global manifest is extended;exact extension and every other original input/product are checked without claiming unchanged whole-manifest replay.

Actual callback value,IRQ/ROM/hardware and final original-layout/OTA compatibility remain unproved. No firmware execution or BIN generation occurs.
