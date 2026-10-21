# OTA page reply: readable C / C++ component

[繁體中文](README.md)

This partial reconstruction implements ID2966 V4.1.60 `9B8E..9C0A`: allocate1026 bytes, write a two-byte page index, request a1024-byte copy through a fresh resident slot, call TX, then tail-transfer to the release slot. Null allocation restores the frame and returns. It does not recover the complete original project.

`src/page_reply.c` owns the algorithm. Native `reply_io.h` supplies narrow register constraints, volatile accesses, actual JAL/JALR calls and a real `musttail`. There is no whole-function assembly or original-BIN instruction template. The input index is full32; only the header truncates to16 bits. Copy source is `u32((0x20004 + liveS1) << 10)`.

Actual C11 and C++17 compiler outputs each contain124 bytes /50 instructions. Two compiler-owned ABI order windows differ. The separately recorded `reply-abi-order/order.py` stage permutes only newly compiled words, changing28 ELF bytes while retaining all metadata and relocations. Its linked124-byte component at9B8E equals the original. This is **C/C++ compilation followed by explicit ABI ordering**, not compiler-only identity.

The verifier first requires strict linking to reject missing `__tsl9v4160_call_8a56`, then uses numeric8A56 in `ADDRESS-WITNESS-ONLY.elf`. No TX-provider bytes are supplied. This component is not complete firmware; this milestone exports no BIN and preserves the existing whole image.

## Offline commands

Run from the project root, with `LLVM` pointing to the verified local LLVM NDK directory:

```sh
sh experiments/tsl9-v4160-ota-page-reply/verify.sh --language both
sh experiments/tsl9-v4160-ota-page-reply/verify_native.sh --tool-dir "$LLVM" --language both
```

Wrappers honor `PYTHON`, otherwise selecting `python3` / `python`. Direct entries:

```sh
python -B experiments/tsl9-v4160-ota-page-reply/verify_host.py --project-root . --language both
python -B experiments/tsl9-v4160-ota-page-reply/verify_native.py --project-root . --tool-dir "$LLVM" --language both
```

Both accept a create-only project-local `--build-root`; `--replay RECEIPT` rechecks actual artifacts without compilation or test execution. Native dependency lookup supports published `analysis/` and working `apk-analysis/`. Exact tool hashes are enforced. Current native evidence uses Windows NDK27.1.12297006; no other platform LLVM build is claimed verified.

HOST passes3 groups /87 cases /3634 assertions plus6 actual compiled behavior mutants per language. It checks full-width index arithmetic, exact effect order, fresh slots, named-call S-register/SP/frame mutations, stopped prefixes, raw versus masked JALR targets and opaque release results. Every positive and negative HOST launch checks executable format and current Python architecture first; RISC-V ELF is refused. Guard code supports PE, ELF and thin Mach-O; actual testing here is Windows. Universal/fat macOS Python is unsupported.

## Limits

HOST is a named algorithm/frame model, not a CPU interpreter. READ/WRITE callbacks may modify synthetic memory and flow; returned callbacks that alter GPRs or their known mask stop with UNKNOWN. Arbitrary register/SP/frame changes are allowed only at named opaque calls. Release keeps raw/masked prepared caller links and an opaque provider result. Nonreturn claims cover committed external-effect prefixes, not a complete physical register prefix.

Broad HOST callback mutation coverage does not prove that native C tolerates arbitrary SP/callee-save destruction. Ordered native byte identity, conditional native ABI and synthetic HOST behavior are separate evidence. Resident-provider ABI, computed interior entries, asynchronous/fault behavior, board, ROM, BLE, Flash and OTA compatibility remain unproved. No RV32 execution, ISA emulation, network or device I/O occurs.

Source evidence, independent native/HOST reviews and selected receipt metadata live under `analysis/v4160-ota-page-reply-2026-10-22/` (working tree: `apk-analysis/tsl9-v4160-ota-page-reply-2026-10-22/`). Generated files/logs stay in ignored local `build/`; published receipt metadata does not imply those archives are published.
