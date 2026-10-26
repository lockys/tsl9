# Message allocation/release: public SDK candidate reconstruction

[繁體中文](README.md)

These are **two public WCH SDK reference bodies**, not ROM read from a TSL9 device. Three original APP allocation sites and four release tails load pointer slots `0x40070` and `0x40068`. The saved header defines these as `tmos_msg_allocate` (slot15) and `tmos_msg_deallocate` (slot13).

Source requires the original register context and explicit assembly ports;it is not a drop-in conventional C API.

| V1.31 candidate entry | Confirmed static observation |
|---|---|
| `0x20000236`,86B | Conditionally RAM-mapped allocation body. A nonzero request passes `(len+8)&65535` and `0xF000 | len` to a heap helper,initializes private header fields and returns the underlying pointer＋8 on the non-null path. |
| `0x431BA`,78B | Flash release body. Null returns5;`payload[-2] != 0xFF` returns4;the other path calls a heap helper and returns0. These numbers do not prove actual release success. |

Observed header writes are a zero word at`+0`,a length halfword at`+4` and byte`0xFF` at`+6`;other bytes are not assumed initialized. The APP's12-byte request conditionally passes20 as the heap helper's length argument. **This is not a complete physical heap-footprint proof.**

Both entries read `0x4002420C`,write zero and execute `FENCE.I`. Every local normal return path includes a restore store,including null paths. MMIO meaning,callee register preservation,IRQ atomicity and physical restoration remain unproved. Ordinary `malloc/free` are not demonstrated replacements.

## Native evidence and version limits

Actual C11/C++17 compilation of [`resident_message_api.c`](resident_message_api.c) produces identical objects:164B/62 instructions,14 positive regions and11 relocations. Re-encoding original addresses reproduces every candidate byte;two independent ELF readers agree. [Summary](summary.json) · [Audit receipt](audit-result-v1.json)

A standard decoder labels two16-bit words as floating-point stores. Saved official LLVM Xwchc formats instead identify `qk.c.sh s0,4(a0)` and `qk.c.sb a5,6(a0)`. Source retains two explicit raw instruction ports. Compiler architecture attributes **do not prove** the physical ISA profile.

The V1.31/V1.40 allocation bodies have identical86 bytes under their separate RAM-copy mappings. Their78-byte release bodies differ in raw form and match only after normalizing one far-call displacement. Actual slot13 values also differ:`0x431BA`/`0x43246`. Underlying heap-helper implementations were not compared;these observations do not establish interchangeable ROM versions.

Two genuine imports,`0x20000040` and`0x20000110`,remain unprovided. No substitutes were introduced. These candidates are not linked into the APP. Formal source remains159 C/H files and APP byte coverage95.54%. No BIN,target/emulator execution,hardware operation or vendor request occurred.

## Local read-only replay

Requires exact saved SDK/header/LLVM references and native outputs. Set `LLVM_BIN` to the local tool directory. This receipt used Windows Android NDK27.1/LLVM18;other platforms remain unverified.

```sh
python3 experiments/tsl9-resident-message-api/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-resident-message-api/build/native-v1
python3 experiments/tsl9-resident-message-api/audit-v1.py --tool-dir "$LLVM_BIN"
```

On Windows,use `py -3`. Prerequisite native outputs and SDK carriers are excluded from this text-only publication. An offline message-status explanation tool may be useful;it is not implemented. These0/4/5 paths must not be confused with the OTA ASCII E acknowledgement.
