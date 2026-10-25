# Secondary message and dispatch candidate

[繁體中文](README.md) · [C/C++ source](secondary_message_dispatch.c) · [Verification summary](summary.json)

Nine original-context bodies from ID2966 V4.1.60 account for **2,048 bytes / 690 instructions**. C11 and C++17 produce identical RV32 objects. Re-encoding 229 direct transfers and seven HI/LO address pairs at their original addresses reproduces every selected CODE byte. Two independent ELF readers agree; conservative static CFGs reach every retained instruction.

| Original range (exclusive end) | bytes | Established structure |
|---|---:|---|
| `0x1264E..0x12660` | 18 | State write and conditional tail calls |
| `0x12660..0x126A0` | 64 | Helper with an opaque ROM-slot tail |
| `0x126A0..0x128FE` | 606 | Seven event cells with six distinct case entries |
| `0x1330A..0x1333C` | 50 | Six existing entries and a ROM tail |
| `0x13F7E..0x13F88` | 10 | Argument adapter to existing `0x13F66` |
| `0x13F88..0x1400C` | 132 | Conditional calls, a callback address and a tail call |
| `0x1400C..0x14056` | 74 | Calls 0x1330A and supplies two callback addresses; excluded neighbor starts at the end |
| `0x15584..0x155D0` | 76 | Counter, scheduling and a 12-byte copy source |
| `0x163AC..0x167A6` | 1,018 | A2 comparison dispatch to existing feature entries |

The event index is `(message[0] - 1) & 255`; the original unsigned guard permits `0..6` before indexing `0x1A58C`. Neither this 28-byte table nor the 12-byte source at `0x19DD4` is supplied as DATA yet. Of 54 compiler UND symbols, 52 name established formal CODE entries and two name those DATA providers. Partial linking and original-coordinate placement remain pending.

An additional dependency occurs in **existing CODE**, at `0x1783A → 0x1AAE8`: the byte index at `GP+370` is used by the load at `0x17844` before modulo reduction. A global bound is unproved. Its contents were not selected; it is separate from the two new DATA UND symbols. Compiler UND counts do not enumerate every runtime dependency.

## Reproduce locally

Set `LLVM_BIN` to an installed Android NDK 27.1.12297006 LLVM `bin` directory; the spec pins tool hashes. From the repository root:

```sh
python experiments/tsl9-secondary-message-dispatch/audit-v1.py
python experiments/tsl9-secondary-message-dispatch/build-v1.py --tool-dir "$LLVM_BIN" --trial local-v1
python experiments/tsl9-secondary-message-dispatch/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-secondary-message-dispatch/build/local-v1
```

`--trial` creates a fresh directory. The C/C++ retains explicit original-register, control, ROM and stack ports and requires the original execution context; it is not a general portable library.

This candidate is not curated into `src/` or the formal coverage measurement. That measurement remains **70,522 / 76,800 bytes = 91.83%**, an address-byte coverage measure rather than feature completion. No BIN was produced; no target, HOST model or ISA execution, hardware access or vendor API request occurred. Startup, ROM ABI, RAM/IRQ and OTA compatibility remain unproved. An offline event/dependency explorer is a potential new tooling feature, not an implementation claim.
