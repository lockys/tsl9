# Scheduled record callback: 0x56CDC

[繁體中文](README.md) · [Previous zero named UND](../tsl9-resident-root-chain-callees/README.md) · [Original scheduler handlers](../tsl9-resident-task-callbacks/README.md)

[C/C++](resident_scheduled_record_callback.c) adds two complete candidate SDK bodies: `0x56CDC..0x56D0E`, **50 bytes / 20 instructions**, and `0x568F6..0x56972`, **124 bytes / 42 instructions**. Both retain their original null and delayed-frame paths, a maximum own frame of 16 bytes, and register context. These are neither HOST APIs nor manufacturer C source.

Actual C11/C++17 objects match: 174 bytes / 62 instructions, 16 FUNC regions, 10 direct relocations and 5 Xwchc ports. Sole import `0x5E3A8` has a real existing body. Unique CODE ownership and independent ELF readers verify **35,324 CODE + 256 DATA bytes / 12,195 instructions**, 2401 FUNC regions, 1914 relocations and 4173 sections. Named UND remains zero.

## How the literal becomes a callback

[provenance-v1.json](provenance-v1.json) revalidates seven complete bodies, **1,158 bytes /407 instructions**, for this conditional provenance:

1. `0x55D00` constructs A0=`0x56CDC`, A1=original record pointer and A3=record+40, restores RA/releases its frame, then tails to `0x43874`.
2. On the original nonzero-helper-result write path, `0x43874` stores `0x56CDC` in selected record word0, the record pointer in word4, and outputs the ID byte. Table slot is `0x2000322C`, stride12, scanned IDs16..47.
3. For `i=16*t+k`, t=1 or2 and `0≤k<15`, handler `0x43326` receiving single event `1<<k` computes the same `table+12*i`, loads word0 as the indirect target and word4 as A0, then calls at `0x43390`.

This requires valid non-overlapping memory, compatible initialization and private ABI, stable table and record words, normal helper returns, and no IRQ or reentrant replacement. The original initializer path with count zero writes task slots 1/2 as `0x43326`; global initialization before dispatch, live binding and timer delivery are not proved.

**Bit 15 takes the message path and returns without this callback invocation.** IDs 31/47 are outside this callback-route proof. Whether original timer or allocation behavior prevents those IDs is unproved, so they are not labelled unusable. Original behavior is unchanged.

## Encoded body behavior

- `0x56CDC` returns directly on zero A0. Otherwise record byte+15 bit 1 selects A1 for `0x568F6`: zero → 62, nonzero → 8. After normal return it writes byte+43=`low8(A0)`, byte+16=0 and byte+40=255.
- `0x568F6` retains three original message calls to `0x5E3A8`, two conditional. It requests record byte+10/+16=0, byte+84=`low8(entry_A1)` and two conditional global clears. Its normal return sets A0=0; **message delivery and hardware success are not proved**. It reads a word at record+288; allocation capacity and ownership remain unproved.

## Whole indirect-transfer inventory

[indirect-inventory-v1.json](indirect-inventory-v1.json) checks actual C/C++ witnesses, original SDK instructions and relocations: 169 return encodings, 146 verified adjacent AUIPC/JALR transfers and **51 register transfers requiring separate binding analysis**. That is not a missing-function count and does not override prior conditional binding proofs. The 61 adjacent literal sequences in candidate numeric regions do not automatically establish function-pointer roles.

Zero UND, conditional provenance and supplied original-PC-tagged bodies do not establish original-address placement or physical execution. Evidence: [audit-result-v1.json](audit-result-v1.json), [evidence-v1.json](evidence-v1.json), [summary.json](summary.json). Original APP remains 159 C/H files and **95.54% static byte coverage**, not functional completion. ROM/RAM/ISA/IRQ, Flash/OTA, callback effects and the 4-byte startup-source gap remain open. **No new BIN or flashability claim.**

## Recheck

Supply the locally retained hash-pinned references,prior artifacts and current native objects first. Nothing is downloaded and no hardware is accessed:

```sh
python experiments/tsl9-resident-scheduled-record-callback/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-resident-scheduled-record-callback/build/native-v1
python experiments/tsl9-resident-scheduled-record-callback/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
python experiments/tsl9-resident-scheduled-record-callback/indirect-inventory-v1.py
python experiments/tsl9-resident-scheduled-record-callback/provenance-v1.py
```

Potential feature:read-only event-route/message-bit diagnostics. Not implemented;no hardware command or assumed allocation policy.
