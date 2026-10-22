# Packet receive: v5 offline machine contract

[繁體中文](README.md)

[packet_receive.v5.c](src/packet_receive.v5.c) covers official ID2966 `[0x16A7C,0x16B0A)`. C11 and C++17 both emit 142B/52 instructions in three genuine architectural regions of 14+116+12B. All 120 noncontrol bytes match. Four JALs and two branches retain **pending relocations**; this is neither a resolved executable function nor flashable firmware.

Checks cover the original frame, incoming A1, then-live S0/S1/S2, A4 DLC arithmetic, rejection A0 and the ring's returned A0. GPIO, masks and ID arithmetic remain C; explicit asm ports retain physical registers, stack and cross-region control. This is a private machine contract, not ordinary C ABI.

```sh
python3 -B experiments/tsl9-packet-receive/verify.py --language c --llvm-bin "$LLVM_BIN" --out-dir experiments/tsl9-packet-receive/build/my-check/c
python3 -B experiments/tsl9-packet-receive/verify.py --language cpp --llvm-bin "$LLVM_BIN" --out-dir experiments/tsl9-packet-receive/build/my-check/cpp
python3 -B experiments/tsl9-packet-receive/verify.py --llvm-bin "$LLVM_BIN" --replay experiments/tsl9-packet-receive/build/my-check/c/verification.json
```

Set `LLVM_BIN` to the existing local tools. Only the recorded Windows NDK LLVM18 producer has been verified; other toolchains require separate validation. No downloads or flag search occur. Use new output directories; Windows can use `python`. Each language passes 41 negative controls. `--require-firmware-ready` must reject with exit 1.

Historical v1/v2/v3/v4 remain unpromoted; [packet_receive.c](src/packet_receive.c) stays v2. v3 repairs initialization order; v4 repairs DLC/A0/ID but both still emit154B with a duplicate epilogue. v5 uses one genuine finish FUNC, without copied original machine code or object-byte patching.

[Current evidence and limits](../../analysis/packet-receive-v5-2026-10-23/README.md) / [earlier evidence](../../analysis/packet-receive-native-2026-10-23/README.md). Raw builds remain local. No target, ISA/MMIO emulation or hardware operation occurred. Full ring/resident ABI, IRQ/fault, chip identity and OTA remain unproved.
