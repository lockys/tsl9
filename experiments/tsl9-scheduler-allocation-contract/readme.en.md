# Scheduler allocation relation (candidate SDK)

[繁體中文](README.md) · [Previous C/C++ bodies](../tsl9-resident-task-final-handlers/README.md) · [Existing BLE initializer](../tsl9-resident-ble-initialization/README.md)

This study traces the prior **48 records × 12 bytes = 576 bytes** index proof to the candidate SDK's actual allocation request. Installed ROM, physical RAM and IRQ compatibility remain unproved.

| Original instructions checked | Encoded relation |
| --- | --- |
| `0x43B90`, `0x43B9A..0x43BB4` | Read unsigned byte `x` at `0x20003201`; compute/store `n=3*((x>>2)+(x&3))+14` at `0x2000319E`. Bit-width reasoning gives `14≤n≤212`, so this expression survives the low-byte store. |
| `0x43BBE/0x43BC2` | Actual AUIPC/JALR target is candidate RAM `0x20000040`, with A0=`576+6*n` bytes and A1=1. The algebraic request range is 660..1848 bytes, without wrap in the allocator's 16-bit rounding recipe. |
| `0x43BC6`, `0x43BCA` | Store the return value at `0x2000322C`. A null result goes directly to restore/return, skipping the following clear and partition assignments. A normal outer return alone cannot prove successful initialization. |
| `0x43BCC..0x43BDE` | Freshly load `n_clear`; request memset of `576+6*n_clear` bytes. |
| `0x43BE2..0x43BFC` | Freshly load `p` and `n_partition`; store `p+576` at `0x200031C4` and `p+576+4*n_partition` at `0x200031E4`. |

Interpreting the request as **576-byte table prefix + 4*n suffix + 2*n suffix** requires equal counts across allocation/clear/partition, an unchanged returned pointer, valid non-overlapping memory and compatible callee/IRQ contracts. Those temporal conditions remain open. Capacity, ownership, lifetime and bounds of all subsequent callback writes are not proved.

## C/C++ and verification

[scheduler_layout.h](scheduler_layout.h) describes original 32-bit numeric words and conditional layout relations. The third record word has no assigned meaning. [scheduler_layout_abi.c](scheduler_layout_abi.c) contains only type/offset/size assertions, with no functions, storage or callable model.

The checker revalidates six existing complete bodies, **1,104 bytes / 386 instructions**, their CFGs and ownership in the current native C/C++ composition. Actual C11/C++17 assertion objects match. Independent ELF readers confirm zero allocated bytes, providers, imports and relocations. No new target CODE or target/HOST-model/ISA/hardware execution occurs.

Evidence: [verification-v1.json](verification-v1.json), [evidence-v1.json](evidence-v1.json), [spec-v1.json](spec-v1.json), [summary.json](summary.json). The candidate composition remains **29,848 CODE + 256 DATA bytes / 4 named gaps**. Original APP static byte coverage remains **95.54%**, which is not functional completion. No new BIN or flashability claim.

## Recheck

Supply the hash-pinned reference inputs, earlier build artifacts, LLVM and local reference directory first. Read-only verification of retained native-v1 artifacts:

```sh
python experiments/tsl9-scheduler-allocation-contract/verify-v1.py \
  --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

For the initial numeric assertion build, add `--build-trial native-v1 --output verification-v1.json`; both names must be absent. The tool downloads nothing and never writes hardware.

Potential future feature: startup diagnostics that distinguish allocation failure from OTA completion and restart verification. This is a research direction; no physical diagnostic channel is implemented or validated here.
