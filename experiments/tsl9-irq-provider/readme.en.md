# IRQ receive-data provider

[繁體中文](README.md)

[irq_provider.v2.c](src/irq_provider.v2.c) reconstructs official ID2966 `[0x18D78,0x18E1C)`. C expresses fresh volatile word reads, shifts/masks and byte/word stores; explicit ports retain cold edges, physical registers and both RETs. Six regions measure18/8/108/10/10/10B. **These are private machine regions, not ordinary C ABI functions or a complete firmware image.**

C11/C++17 v2 nominal measurements are164B/53instructions, with the whole code span equal to the original, SHA256 `678a3cbf42bc02d5c730973675858a18e538af9fdc1cb74dd9296f220f487ae3`. Native has3RVC relocations to genuine definitions; the standalone nominal link resolves them with no UND/RELA.

v1 also measured164B, but its bank-return LW used A1 before OR into A5, changing original A1 preservation. Nominal byte differences were at134/138/154/158. v2 adds an A5 value port after each bank word read. Failed source/raw local receipts remain unchanged; v1 is not classified as equivalent.

```sh
python3 -B experiments/tsl9-irq-provider/probe.py --version 2 --llvm-bin "$LLVM_BIN" --out-dir experiments/tsl9-irq-provider/build/my-probe
```

Use fresh directories and existing local LLVM; Windows may use`python`. Only the recorded Windows NDK LLVM18 producer was tested. Other OS/toolchains are unverified. No tool download, flag search or target execution occurs.

See the [earlier static boundary](../../analysis/ring-irq-adapter-2026-10-23/provider-next.en.md) for dataflow/unknowns and [current analysis](../../analysis/irq-provider-2026-10-23/readme.en.md) for formal/integration results. Physical MMIO identity, IRQ context, ring's dynamic resident call and complete startup/memory/hardware/OTA remain unproved. No complete firmware BIN was produced.
