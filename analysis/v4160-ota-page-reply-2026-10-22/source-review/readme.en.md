# OTA page reply: original raw-source contract

[繁體中文](readme.zh-TW.md)

This review covers original ID2966 V4.1.60 `0x9B8E..0x9C0A`: exactly 124 bytes and 50 RV32I/C instructions. `source-proof.py` independently decodes instruction fields and compares all operands and ordering to an explicit contract. It does not interpret instructions or execute firmware. All 18 operand/order controls are rejected by the decoder/contract, rather than merely failing the whole-image hash.

`source-proof.json` retains a successful original-carrier readback. `retained-evidence.json` carries only the relevant raw rows and normalized symbol/RELA evidence from the prior protocol review and original 8280-RELA carrier. The selected original image SHA256 is `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`; this interval is `5171c6d96b0151461524f4719cc96d8151e0fec5196a591d5ecc516b82a15198`.

## Source behavior and exact boundaries

`contracts.json` records the ordered saves, fresh pointer loads, individual call arguments, byte stores, fresh restores and terminal edges with exact PCs. The function takes opaque context A0, opaque command A1 and **full 32-bit index A2**. At `9BAC`, S1 receives A2 without narrowing. Only the header retains its low 16 bits; the copy-source formula uses the full live S1: `u32((0x20004 + S1) << 10)`. A u16 C interface would silently strengthen this entry contract.

The 32-byte frame starts at `9B8E`. S2 is saved before the allocator pointer is read at `9B96`; all remaining saved registers follow that pointer read. `9BAE` calls the allocator slot with A0=1026. A zero return branches to `9BFA`, performs six fresh frame reads, increments live SP and returns through freshly restored RA. A1..A7 retain opaque allocator residues; no common status return is synthesized.

On the nonzero path, `9BB6` stores the low index byte at allocation+1 **before** `9BBA` stores the high byte at allocation+0. `9BC2` freshly loads the copy target from live S2+0x4C, then `9BD4` requests 1024 bytes from the numeric source to allocation+2. `9BE0` calls TX at `8A56`, using live S3/S4/S0 and length1026. Copy and TX results have no local status branch.

The release path is a **tail transfer**, not an ordinary local call followed by a normalized return. `9BE4` selects A0 from live S0 before `9BE6` restores S0; `9BE8` reads the release slot from live S2+0x68 before S2 is restored. The remaining fresh stack reads restore RA/S1/S2/S3/S4, live SP is increased by32 and `9BF8` jumps through T1 without linking. A1..A7 are TX residues. The release callee determines any eventual return/result.

Every frame access uses live SP; pointer loads use live S2; post-call dataflow uses live S0/S1/S3/S4. Unknown callees may change registers, alias frame memory, transfer or never return. Preservation of SP/S registers is a **condition for a particular native profile**, not a fact established by this local source. Fresh restore words may differ from initially saved words. A null function slot is not guarded and must not be confused with an allocator returning zero.

For halfword `8297`, the independent fields are C.JALR **rd=x1, rs1=x15**. The old retained ESIL assignment to A5 is inaccurate and is not consumed. Direct local register destinations are listed separately from opaque callee effects; the list does not prove those other registers are preserved.

## Symbols, references and portable replay

The original section is AX/PROGBITS, align2, size124. Its public `__tsl9v4160_ota_code_9b8e` symbol is GLOBAL NOTYPE size0; there is no existing canonical FUNC124 provider. Two owned relocations cover the null branch and TX JAL. One external recorded RVC_JUMP at `9DF4` enters offset0: it is the shared physical W/R tail edge. The local null label is at offset108. No external recorded relocation targets that interior label in this carrier; computed, encoded or ROM interior references remain unknown. Future integration must explicitly preserve or discharge these exact roles.

Run from the project root; published `analysis/` and workspace `apk-analysis/` layouts are supported for the immutable parser reference:

```sh
python3 -B apk-analysis/tsl9-v4160-ota-page-reply-2026-10-22/source-review/check-review.py --project-root . --firmware exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin
```

The shell wrapper accepts the same arguments; set `PYTHON` if needed. Default replay rechecks raw instructions, all18 controls and source-manifest/retained role bindings. It explicitly reports **no actual archived-carrier replay**. Optional `--object ORIGINAL.o` independently reparses its actual relevant symbols and relocations using the pinned portable ELF parser. Selected historical proof and a fresh actual archive readback are separate evidence levels. No generated build object is a publication-seal member.

This source-only seal proves neither reconstructed C/C++ behavior nor native placement, exact asynchronous/fault prefixes, installed ROM/BOOT identity, hardware behavior or BLE update compatibility. Those require separate implementation and integration evidence. No target execution, emulator, network request or physical I/O occurred.
