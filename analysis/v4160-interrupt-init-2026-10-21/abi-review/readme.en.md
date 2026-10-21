# ID2966 initialization ABI review

This independent audit covers original runtime SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`, base `0x8000`, entry `0x9A42`, and four direct helpers. It reads original bytes and static RISC-V disassembly. It does not execute original instructions, emulate an ISA, access hardware, or prove OTA compatibility.

## Confirmed source behavior

`0x9A42..0x9AD2` is 144 bytes / 46 instructions. Helpers `0x19124`, `0x19142`, `0x19160`, and `0x1917E` each occupy 30 bytes / 12 instructions. The aggregate scope is 264 bytes / 94 instructions. `audit.py` checks original identity, contiguous instruction coverage, per-instruction original bytes, six direct call targets/continuations, CSR operands, stack prologue/epilogue, and the existing main-entry native capture. Its JSON output retains the exact source rows.

The entry subtracts 16 from SP and stores S2, S1, S0, and RA at offsets 0, 4, 8, and 12. Source PC `0x9A50` clears CSR `0x800` bits `0x88`; PC `0x9AC2` sets those bits. This does **not** save and restore the incoming CSR value. Calling these operations interrupt masking is a hardware interpretation, not established by the instruction operands alone.

| Call PC | Helper | Fresh 32-bit RMW address | Mask | Operation |
|---|---|---|---|---|
| `0x9A5E` | `0x19142` | `0x4002101C` | `0x02020006` | OR |
| `0x9A6A` | `0x19124` | `0x40021018` | `0x0000101D` | OR |
| `0x9A74` | `0x1917E` | `0x40021010` | `0x02020006` | OR |
| `0x9A7E` | `0x1917E` | `0x40021010` | `0x02020006` | AND with complement |
| `0x9A88` | `0x19160` | `0x4002100C` | `0x0000101D` | OR |
| `0x9A92` | `0x19160` | `0x4002100C` | `0x0000101D` | AND with complement |

Each helper branches on whether A1 is zero; it is not an equality-to-one test. Each call reads the addressed word again, including clear after set. A cache of the first word is not equivalent when the external register value changes. The final clear at `0x19172` reads the word, `0x19174` complements A0, `0x19178` computes the AND, and `0x1917A` writes the result.

After the six helper calls, source performs these six ordered writes: byte `0` to `0xE000E42D`; word `0x2000` to `0xE000E104`; byte `0x20` to `0xE000E424`; word `0x10` to `0xE000E104`; byte `0x30` to `0xE000E427`; word `0x80` to `0xE000E104`. The three writes to the same word address are independent stores, not a merged value or read-modify-write. No fence or delay instruction appears in this scope.

## Minimal readable C seam

A suitable semantic seam is `uint32_t init_9a42(const io_ops *io)`, with synchronous `read32`, `write32`, `write8`, `csr_clear`, and `csr_set` operations. Its return value preserves the source's final A0 word: the **sixth fresh read**, AND `0xFFFFEFE2`. The source does not explicitly assign a C-level success status. A `void` semantic interface discards this observed A0 value. An implementation may choose a separate status for hosted testing, but must label it an added host contract.

The same business logic can use a recording, ordinary-memory backend in host tests and a separately compiled native backend with volatile, width-specific MMIO access plus custom CSR instructions. On the native backend, CSR assembly should be volatile with a compiler memory clobber to keep the surrounding C accesses ordered at compilation. A compiler barrier is not a hardware fence and does not establish bus ordering, interrupt semantics, privilege availability, or physical effects.

## ABI and environment limits

On the uninterrupted, normally returning source path with unchanged stack memory, S0/S1/S2 and RA reload from their original slots and SP returns to its entry value. These are **fresh stack reads**, not immutable snapshots: external stack/SP modification changes subsequent loads and return control. Immediately after the final ordinary helper return, A0 contains the masked fresh word. At entry return, A1 is 0, A4 is `0x80`, A5 is `0xE000E000`; other non-saved GPRs are unchanged by this scope. There is no store to GP-relative RAM here.

Ordinary C can preserve standard call-boundary requirements and return the observed A0 value. It cannot promise source-identical caller-saved register residue, fixed save-slot addresses/order, instruction PCs, exact prologue size, custom interrupt entry/return conventions, or interaction with an asynchronous handler. Standard C does not expose the source SP/RA machine state. Native code must be audited after compilation before making even compiler-specific register claims; compilation alone cannot prove the original installed environment.

Do not use C cleanup to set the CSR bits after an injected host error unless that behavior is explicitly a host contract: the original straight-line source has no such error-return path. A host trace stopping at a failed operation proves only the completed prefix. MMIO reads/writes are not atomic as a pair; this audit does not identify the device's register names, reset effects, or read side effects.

Run `audit.py --image <original-BIN> --r2 <radare2-executable> --native-capture <initialization_native.c>` to emit retained JSON. Static checks prove this bounded source correspondence, not an executable native replacement or a flash-ready image.

