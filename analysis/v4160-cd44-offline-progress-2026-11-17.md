# v4.1.60: offline 0xcd44 investigation

Reference: decoded ID-2966-V4.1.60 BIN, 76,800 bytes, SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`. Addresses below assume a linear image base of `0x8000`.

## Getter

At `0xcd44`, bytes `17f5ff1f0345251e8280` decode to PC-relative address formation, an unsigned byte load, and return. The computed address at this placement is `0x2000bf26`. A standalone pure-C volatile-byte getter compiled with the investigated C11/C++17 project profile instead produced `37c50020034565f28280`: it uses absolute address formation, reads the same nominal byte at this placement, but is **not byte-identical** and has not been integrated. In a synthetic fault-boundary model the intermediate `a0` is `0x2000bd44` for the original versus `0x2000c000` for the candidate; this is not a hardware trap experiment.

## Writer and callers

The original `0xc7aa` entry computes the same nominal address, and the byte store at `0xc7ae` stores the low eight bits of `a0`. The following branch tests the full 32-bit register: input `0x100` writes zero while selecting the nonzero branch. A bounded synthetic model traces a direct caller beginning at `0xcc8c` through the call and stops at that branch. `rasm2` was used separately for a static instruction/target cross-check. Other caller continuations into `0xcd44` were separately modeled within bounded windows.

The local regression scripts compared the 256 byte values for the getter, exercised caller memory-event ordering and negative mutations, and passed in ordinary Python and Python `-O`. The scripts and diagnostic build artifacts are not included in this report and remain subject to separate publication and dependency review; this report alone is not a self-contained reproduction package.

## Limits

Synthetic memory, injected contexts and successful instruction models do not prove actual reachability, physical RAM ownership, field meaning, concurrent behavior, ABI compatibility or hardware fault semantics. Word-store fault atomicity in the caller model is a synthetic policy. These findings do not establish a complete C reconstruction or a flashable image.
