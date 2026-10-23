# Queue consumer and conditional dispatch

[繁體中文](README.md) · [Source](src/queue_consumer.v3.c) · [Original instruction evidence](../../analysis/irq-provider-2026-10-23/next-consumer.json)

This reconstructs V4.1.60 `[0x12C58,0x12D92)`, including reachable cold blocks after RET. Actual C11/C++17 candidates each contain314B/107 instructions across10 genuine private regions. Every bit outside the25 unresolved relocation immediate fields matches the official input. These are private architectural regions, not10 ordinary C functions or complete firmware.

C owns zero extension, constants, a fresh indirect byte read and its mask. Explicit ports preserve the frame, physical saved registers, SP/CSR and control edges. Post-resident operations read then-live S0..S7/SP; A1/A2 are not reset before12D72. Resident identity is unknown, rather than assumed to be memcpy.

Versions1/2 retain failed compiler evidence: LLVM rejected label-based `.reloc` sites beside relaxable fragments. Version3 uses native `jal ra,symbol` and current-position-relative `.reloc .-2/.-4` expressions. It supplies no provider addresses or opcode arrays.

```sh
python3 -B experiments/tsl9-queue-consumer/probe.py --version 3 --out-dir experiments/tsl9-queue-consumer/build/my-new-probe
```

The output directory must be new. The probe uses one pinned local LLVM profile and downloads nothing. `build/probe-v3-lf/measurement.json` is a measurement, not a formal semantic verdict. Its ET_REL retains eight genuine UND providers and25 relocations; it is not a BIN. No target/ISA/MMIO execution occurred. Hardware, complete IRQ/resident ABI and OTA compatibility remain unproved.

The formal [verify.py](verify.py) receipts are `build/verified-v3/{c,cpp}/verification.json`. Public [C](../../analysis/queue-consumer-2026-10-23/receipts/queue-c.json)/[C++](../../analysis/queue-consumer-2026-10-23/receipts/queue-cpp.json) copies are byte-identical to these original portable receipts. Each language rejects295 controls:264 reparsed raw ELF,8 typed rows,18 SSA/port,2 full-IR and3 MD mutations. Whole-ELF pins are disabled for every control;293 also disable the full-IR pin. The230B count covers complete noncontrol instructions;2163 retained bits also include operands in control instructions.

```sh
python3 -B experiments/tsl9-queue-consumer/verify.py --replay experiments/tsl9-queue-consumer/build/verified-v3/c/verification.json
```

Adding `--require-firmware-ready` rejects with exit1 because calls and physical compatibility remain unresolved. The source has canonical trailing LF; curated [src/native/receive/queue_consumer.c](../../src/native/receive/queue_consumer.c) is byte-identical to current v3. Earlier source/v1 receipts remain local. Formal v3 and curation v4 are fresh compiler runs, not rewritten original receipts.
