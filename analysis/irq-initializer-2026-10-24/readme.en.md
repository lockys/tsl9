# Original IRQ initialization and RCC helpers integrated

[繁體中文](README.md)

The [selected C/C++ source](../../src/native/irq/irq_initializer.c) reconstructs the complete `9A42–9AD2` initializer,**144B/46 instructions**,plus four30B RCC helpers at `19124/19142/19160/1917E`. All **264B/94 instructions,19 private regions and10 control relocations** match original-coordinate encoding in C11/C++17,with no external dependencies. Main-component UND decreases **92 → 91**.

The original16B frame,S2/RA/S0/S1 save order,CSR `0x800` mask `0x88` clear/set,six real helper calls,six byte/word MMIO writes,and register/SP restore order are retained. This preserves instruction order without claiming physical CSR meaning,restoration of prior CSR state or asynchronous IRQ equivalence.

| Current main component | Result |
| --- | --- |
| Code/data | 14,524B/674B;1,246 sized code owners and71 retained aliases |
| Native partial link | 961 relocations/91 genuine UND;no ABS function providers or stubs |
| Original addresses | All **15,198B** match the official BIN after actual native linker placement |
| Static positions | 5,049 instructions/836 direct transfers;4,645 ordinary next and292 potential call-return positions are owned |
| Still unknown | 226 register-indirect transfers,10 MRET destinations,and8034 EBREAK resume behavior |
| Source organization | 101 C/H files,74 code units plus1 data unit;150 comparisons/300 objects total |

Original reset instructions at `18710–18720` form `0x803B` from the `0x8038` table base and write MTVEC. Table slots45/36/39 contain `979E/12C24/16FB6`;the latest diagnostic ELF retains three typed vector references to genuine reconstructed code. Priority-style byte offsets45/36/39 correspond numerically to one-bit positions13/4/7. Physical controller bank/index semantics and peripheral identities remain unproved.

The earlier180B `interrupt_registers.c` initializer stays preserved outside the active component. The new layout remains a **non-loadable diagnostic ET_EXEC,entry0,PT_NULL only,zero PT_LOAD segments**,rather than an OTA BIN. Its91 hidden local NOTYPE ABS constants preserve unknown-reference addresses without function bodies.

[Summary and ordered operations](summary.json) · [Original static evidence](evidence.json) · [Source proof](../../experiments/tsl9-irq-initializer/build/source-proof-v1.json) · [Component receipt](../../experiments/tsl9-irq-initializer/build/component-v1/measurement.json) · [Original-address receipt](../../experiments/tsl9-original-layout/build/irq-initializer-v1/measurement.json) · [91 missing providers](next-providers.json)

Replay from the project root using the already-installed,pinned LLVM directory:

```sh
python3 experiments/tsl9-irq-initializer/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-irq-initializer/build/component-v1
python3 experiments/tsl9-original-layout/build-v7.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/irq-initializer-v1
python3 experiments/tsl9-original-layout/verify-flow-v6.py --replay experiments/tsl9-original-layout/build/irq-initializer-flow-v1
```

Next:the shared `181C4` provider and actual dependencies. An offline IRQ-startup map now retains CSR/call/write/vector facts;read-only live interrupt diagnostics remain a candidate,with no new device feature added.

The full76,800B image,physical MCU/controller,installed resident,RAM/private ABI,asynchronous IRQ and OTA remain unproved. No target/HOST-model execution,ISA emulation,hardware/network access,BIN generation,commit or push occurred. Historical personal information remains unresolved;earlier receipts are preserved.
