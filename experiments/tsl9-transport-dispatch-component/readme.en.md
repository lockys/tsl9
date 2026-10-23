# Actual partial link of dispatch and transport

[繁體中文](README.md)

This experiment runs existing LLVM `ld.lld -r --no-relax` on two formally checked real objects: the526B queue/filter/small-provider dispatch.o and280B transport native.o. C and C++ retain their own actual upstream proofs. There is no new compilation, adapter, wrapper, stub, ABS provider, executable image or BIN.

`.transport_dispatch` retains dispatch at0..526 and appends all13 transport regions at526..806. The checker requires806 bytes,280 instructions,32 genuine FUNCs (30 private architectural regions and two small ordinary C functions),41 pending RELA, five strong UND and zero global ABS. All cold/post-RET regions remain.

The original filter C.JAL reference at combined offset464 now binds the genuine `tsl9_filter_external_8a56` FUNC at526. This resolves a symbol definition; all41 machine control relocations remain pending in ET_REL. Raw targets are not reported as executable resolved transfers. Remaining providers are `9454`, `9b36`, `12abe`, `12a08`, `14d2e`.

The checker freshly replays both upstream formal proofs, including source/IR/SSA/typed operands/MD/recipes/tools/resources. It uses the sealed independent ELF32 parser and new join checks for all body bytes, genuine symbol ownership, relocation remapping, complete allocation and280 LLVM raw rows. Five source spans are freshly read from the original V4.1.60 image; all non-control bits and typed RD/RS/C.JAL link/original destinations must match. Actual in-memory ELF/operand controls exercise these gates without a whole-object hash shortcut.

From the project root, set `LLVM` to the existing LLVM bin directory:

```sh
python experiments/tsl9-transport-dispatch-component/check.py
python experiments/tsl9-transport-dispatch-component/build.py --project-root . --llvm-bin "$LLVM" --dispatch-root experiments/tsl9-queue-dispatch-component/build/component-v1 --transport-root experiments/tsl9-transport-frame/build/verified-v1 --build-root experiments/tsl9-transport-dispatch-component/build/NEW
python experiments/tsl9-transport-dispatch-component/check.py --project-root . --llvm-bin "$LLVM" --replay experiments/tsl9-transport-dispatch-component/build/NEW/c/verification.json
```

Default is source metadata only. `--folder MODE --receipt NEW` creates a new actual review; `--replay` is read-only. `--require-firmware-ready` must exit1. Receipts use `${TSL9_ROOT}`/`${LLVM_BIN}`; sources/POSIX wrapper have no hardcoded personal path. Previously denied Git Bash is not retried; sh runtime remains unverified.

Open dependencies include five external providers, two fresh admission targets from `[0x4013C]`, the resident tail from `[0x40050]`, and other opaque queue/filter calls. VMA0 does not preserve original-placement AUIPC meaning. Opaque callees can change then-live S0 after the initial length guard. No ordinary C ABI, complete ROM, IRQ/fault/asynchronous, physical placement, hardware or flashing proof is claimed. No target/ISA/MMIO/HOST/network/hardware execution occurs. Firmware-ready, installed-ROM and physical-placement gates remain false.
