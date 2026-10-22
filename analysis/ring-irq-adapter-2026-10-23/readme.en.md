# 52B ring IRQ adapter

[繁體中文](README.md)

Official ID2966 `[0x12C24,0x12C58)` is reconstructed as [C/C++ machine regions](../../src/native/irq/ring_irq_adapter.c). Five regions measure14/10/18/6/4B, totaling52B/17 instructions with42 original noncontrol bytes. **Three control immediates remain pending; this is not full52B equality, ordinary C ABI or flashable firmware.**

Confirmed local flow:

1. A0=`0x40006400`; fresh LW32 `[A0+12]`, mask3. Zero branches to MRET at`0x12C54` without creating a frame.
2. Nonzero subtracts32 fromSP, setsA2=SP+12 thenA1=0. JAL at`0x12C38` calls`0x18D78`, withRA continuation`0x12C3C`.
3. After that provider returns, then-live SP supplies LBU A2,+22, LHU A0,+12 and A1=SP+23; A3=0. JAL at`0x12C4A` calls ring`0x12BC8`, withRA continuation`0x12C4E`.
4. After ring returns, then-live SP+=32 and MRET at`0x12C50`. The adapter itself has no RA save/restore or ordinary RET.

v1 exposed SP as a C address value. LLVM emitted two extra moves, one writing SP, producing54B/19 instructions; the52B linker contract rejected it. v2 uses physical SP access ports. Failed source/raw local measurements remain unchanged.

`component.ld` produces partial ET_REL with3RELA: offset12 RVC branch to the real empty FUNC, offset20 JAL to UND18D78, and offset38 JAL to UND ring. Ring has separate reconstruction/nominal evidence, but remains explicitly UND in this standalone object. No ABS/raw-byte fake provider was substituted. The prior586B nominal graph is unchanged; IRQ is not yet integrated into a resolved executable graph.

Replay requires retained local build artifacts; public JSON alone cannot recreate the whole build directory:

```sh
python3 -B experiments/tsl9-ring-irq-adapter/verify.py --llvm-bin "$LLVM_BIN" --replay experiments/tsl9-ring-irq-adapter/build/verified-v2/c/verification.json
python3 -B scripts/verify-curated-source.py --replay build/curated-source/ring-irq-20261023-v2/verification.json
```

Windows may use`python`. Tools are existing local NDK LLVM18; other OS/toolchains remain unverified. [summary.json](summary.json) records the formal checker, receipts, negative-control classifications and actual outcomes. `--require-firmware-ready` rejects incomplete whole-device proof.

Curated`src/` now has52C/header files and26native units. C11/C++17 origin/curated compilation passed52comparisons/104objects. All50prior results and301artifact hashes remain unchanged. The new receipt contains106inputs,313artifacts and104recipes/MD files.

Formal C/C++ receipts use variable paths and public copies are byte-identical. [curated-source.json](receipts/curated-source.json) is an explicitly labeled public path derivative. The raw original remains local, SHA256 `8736e11ca4f0b7f1368eab4531a39e92f564996eb9e47343349094575740ef80`. Only path strings/dictionary keys changed; inverse JSON equality was checked. Direct original-receipt replay is not claimed for the derivative. Original BIN/APK bytes, frozen historical derivatives and Git history were not rewritten.

Next is the [readable C reconstruction of the164B provider](provider-next.en.md). Local SP preservation, fresh word reads and length/field dependencies are static leads; full IRQ context, resident/MMIO identity, silicon and OTA remain unknown. No target/ISA/MMIO, hardware or third-party API execution occurred. No complete firmware BIN was produced.
