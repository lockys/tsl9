# Callback-slot installation, joins and clearing

[繁體中文](README.md) · [Previous APP task](../tsl9-original-APP-task-binding/readme.en.md) · [Existing RF C/C++](../tsl9-original-RF-tx-path/readme.en.md) · [Existing callback C/C++](../tsl9-resident-state8-callbacks/readme.en.md)

This study checks **17 complete SDK functions / 5,602 bytes / 1,962 instructions** and joins three additional sites. Cumulatively **39 / 51 sites** have at least one evidenced conditional domain; 12 remain unjoined. This does not resolve every possible target and is neither a missing-function count nor functional completion. [Ledger](ledger-v1.json) · [Receipt](verification-v1.json)

## One slot, seven evidenced installation contexts

Setter `0x2000078A` writes A0 to `0x20002EF8`. Nonzero A0 also sets byte `0x20002EFC` to 1. Five registration sites have seven literal sources:

| Registration call pair | Last A0 definition | Installed target |
| --- | --- | --- |
| `0x64534` | `0x64530` | `0x645DC` |
| `0x64962` | `0x64954` | `0x65DE6` |
| `0x64E8E` | `0x64E8A` | `0x6448E` |
| `0x64E8E` | `0x64EFA` | `0x64422` |
| `0x65102` | `0x650FE` | `0x653A0` |
| `0x65102` | `0x6515E` | `0x65164` |
| `0x65508` | `0x65504` | `0x65620` |

Two sites join distinct branches and cannot be described by one value. The verifier computes A0 may-reaching-definitions over complete CFGs: callees conservatively clobber A0, joins union definitions, and unmodelled writers stop verification. Independent raw LUI/ADDI decoding verifies all seven last definitions; they exactly cover the definitions reaching these five call pairs. This is finite static dataflow, not target execution or concrete machine-state emulation.

Every target has a complete existing native body. A target is bound to consumer `0x200007B4` only if its producer reaches the setter and the slot remains unchanged until the load. Other installers, dynamic inputs and actual ordering remain unresolved. No ordinary `void(void)` callback ABI is proved.

## Clearing after return

Consumer `0x200007A0` guards the pointer before calling at `0x200007B4`. It **reloads the flag** at `0x200007BA` after return:

- Zero clears the then-current pointer slot at `0x200007C4`.
- Nonzero skips clearing.

Installing A0=0 clears only the pointer; **it does not zero the flag**. One path in `0x60516` sets A0=0 at `0x60734`, releases its 32-byte frame and tails through AUIPC-T1/JALR-zero to the setter. Preserve the no-link transfer; this is not a normal call or a statement about all returns from that function.

Other flag writers are not closed. Neither unconditional one-shot behavior nor guaranteed callback-replacement protection is established.

## A separate optional callback array

This differs from slot `0x20002EF8`: base=`0x200031C8`, five four-byte entries. Initialization requests clearing `[0x200031C8,0x200031DC)`; actual completion and live zero values were not observed.

- Slot2 `0x200031D0`: after the expected clear or actual cleanup tail `0x657C2 → 0x43B28` with A0=0/A1=2, a stable zero makes guard `0x2000081C` skip `0x2000081E`.
- Slot0 `0x200031C8`: after the expected clear or a prior normal callback followed by zero-store `0x2000093E`, a stable zero makes guard `0x2000093A` skip `0x2000093C`.

Slot0 **writes zero directly after normal callback return, without a replacement-flag check**. Do not merge it with the earlier slot's fresh-flag policy. Other unguarded array sites remain unresolved.

All results require matching ROM/ISA/RAM, valid disjoint memory, the original full register/stack/private ABI, normal returns and no IRQ/reentrant overwrite during binding. No live binding was observed.

Existing C/C++ bodies are retained. No target CODE/DATA, compilation or BIN was added. The candidate remains **35,324 CODE + 392 DATA bytes / 12,195 instructions / 0 named UND**. The APP's 159 C/H files and **95.54% static byte coverage** are unchanged. The four-byte startup-source gap and hardware/Flash/OTA compatibility remain unresolved. **This is not flash-ready firmware.**

A possible feature is offline callback-source and flag/clear-path diagnostics. No UI or hardware control was added.

```sh
python experiments/tsl9-resident-callback-slot-binding/verify-v1.py --tool-dir "$LLVM_BIN"
```
