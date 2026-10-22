# Ring interrupt adapter

[繁體中文](README.md)

[irq_adapter.v2.c](src/irq_adapter.v2.c) reconstructs official ID2966 `[0x12C24,0x12C58)`. Its curated copy is [src/native/irq/ring_irq_adapter.c](../../src/native/irq/ring_irq_adapter.c). C expresses the32-bit status read/mask and tag0; explicit machine ports preserve the conditional frame, then-live SP accesses, genuine JALs and both MRETs. **These are not ordinary C ABI functions or flashable firmware.**

v1 imported SP as a C value. LLVM emitted extra A1 moves and wrote SP, yielding54B/19 instructions; the52B partial-link assertions rejected it. Failed source/raw local evidence remains unchanged. v2 uses physical SP load/address ports and measures52B/17 instructions with42 original noncontrol bytes. Three control immediates remain pending; this is not full52B equality.

```sh
python3 -B experiments/tsl9-ring-irq-adapter/probe.py --version 2 --llvm-bin "$LLVM_BIN" --out-dir experiments/tsl9-ring-irq-adapter/build/my-probe
```

Use fresh output directories and existing local LLVM. Only the recorded Windows NDK LLVM18 producer was tested; Windows may use`python`. Other OS/toolchains remain unverified. No downloads, flag search or target execution occurs. `component.ld` produces only partial ET_REL with3RELA and2genuineUND providers,18D78 and ring.

See [current analysis](../../analysis/ring-irq-adapter-2026-10-23/readme.en.md) for full evidence/limits. The [next164B provider boundary](../../analysis/ring-irq-adapter-2026-10-23/provider-next.en.md) is static research, not readable C implementation or physical chip identification.
