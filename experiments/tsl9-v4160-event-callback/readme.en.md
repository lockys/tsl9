# Readable event callback reconstruction

[繁體中文](readme.zh-TW.md)

The shared C11/C++17 algorithm reconstructs ID2966 V4.1.60 callback `0x8614..0x888C`, originally 632 bytes / 217 instructions. Memory primitives retain volatile widths and fresh reads; resident slots remain raw numeric interfaces. No original opcode template, target execution, ISA emulation, network/hardware I/O or new BIN is used.

Priority is mask `0x8000` (LOW16 sign), mask `0x8`, full32 context versus fresh task byte, then masks `1`, `2`, `4`. Returns use the live complete event word XOR the selected mask. One gate requires exactly 1; another accepts the low bit. Capacity wraps after subtracting 3 to16 bits. Pending difference wraps to16 bits then has a signed16 positivity test. Shared source preserves memory widths, post-allocation store before the null branch, fresh count updates and copy/send/release order.

```sh
python -B experiments/tsl9-v4160-event-callback/verify.py --language both
python -B experiments/tsl9-v4160-event-callback/verify.py --kind native \
  --tool-dir /path/to/pinned/LLVM --language both
```

The POSIX `verify.sh` accepts `PYTHON=/path/to/python`. HOST is the default and needs no RISC-V LLVM. Explicit build roots must be new paths inside this model's build folder; the default uses a UUID. Only pinned Windows NDK LLVM was actually validated.

```sh
python -B experiments/tsl9-v4160-event-callback/verify.py --replay HOST_RECEIPT
python -B experiments/tsl9-v4160-event-callback/verify.py --kind native --replay NATIVE_RECEIPT
```

Each HOST language has twelve cases, 34 checks and five actually compiled semantic negatives. Every executable launch passes the immutable native-machine guard. Only opaque-call providers may mutate named carried values/argument residues. Memory-callback mutations become UNKNOWN. Synthetic saved-frame restores read fresh memory, including changed live SP. HALT/TRANSFER/UNKNOWN stop without invented cleanup. A HOST diagnostic budget is not a native timeout.

The argument mask is an explicit algorithm-call projection, not complete physical GPR-prefix proof. `return_address` is saved-frame bookkeeping, not the architectural RA for each resident call. The model does not execute restored addresses or interpret CPU state.

One bounded native-only `always_inline` change reduced the corrected 944+90=1,034-byte baseline to one real FUNC658 / 241 instructions, frame48, fifteen opaque JALRs, no UND/libcall stubs. It still exceeds original632 by26 bytes. Placement, full original ABI, physical register mappings, call-return PCs and asynchronous/fault equivalence remain unproved. The new compiler saves S10 at original-unused SP+0 and changes save order.

`COMPONENT-ONLY-NOT-FIRMWARE.elf` links at scratch VA0x1000. Conventional callee preservation is conditional; HOST handling of arbitrary named S/SP/GP mutations does not prove native realization. This milestone changes no existing full image, exports no BIN, and proves no physical flashing or OTA compatibility.
