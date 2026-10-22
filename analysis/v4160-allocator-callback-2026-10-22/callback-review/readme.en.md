# Configuration ownership of the allocator callback word

[繁體中文](readme.zh-TW.md)

**An actual conditional writer is identified: a64-byte configuration copy places field+52 exactly at the word loaded by the allocator.** Neither absence of a direct-address SW pattern nor startup zeroing establishes its later value. No callback function identity, lifetime, installed resident or ambient-A2 independence is proved.

This is offline static evidence from the two existing SDK HEX/segments and official ID2966. No downloads, compilers, HOST runs, RV32 execution/emulation, hardware or generated providers/BINs occurred.

| Item | V1.40/carrier | V1.31/carrier-dec2023 |
|---|---|---|
| Actual slot400A4 word |43D0A|43C7E|
| Bounded initializer prefix |43D0A..43D7C,114B/41rows|43C7E..43CF0,114B/41rows|
| Config destination, conditional on liveS0 |2000323C|200031EC|
| Destination+52 / allocator callback word |20003270|20003220|
| Zero-helper source |402D2..402F0|40292..402B0|
| Mapped zero helper |RAM20000022..20000040,30B/9rows|same|
| Conditional zero interval |[20002F48,20003668)|[20002EF8,20003618)|

Existing sealed resident-entry and allocator-review pin the initialization mapping, original sparseHEX and contiguous segment hashes. The official Runtime SHA256 is `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`; its90B original caller13B4C..13BA6 is reread to retain the ambient source-pointerA2 boundary at13B68.

## Bulk copy supplies the word

The initializer snapshots the config pointer inS1 and performs an earlier numeric call to200004BC. On the accepted branch it setsS0=20003000. Main43D5A/historical43CCE setA0=liveS0+23C/+1EC, A1=0, A2=64 and call2000039C, also the actual slot40048 word. This establishes a zero request, not unconditional completion/preservation.

Main43D66..43D74/historical43CDA..43CE8 then freshly setA2=64,A1=liveS1,A0=liveS0+23C/+1EC and call20000332, the actual slot4004C word in both candidates. Its58B/18instruction forward-byte-copy leaf is already sealed in compact/callee-review. Under normally completing accesses, the appropriate candidate/profile/mapping, suitable liveS0/S1 and no adverse aliases/interference, the four sequential source bytes at config+52..55 populate the allocator callback word. This is not an atomic READ32 snapshot or an entry-register preservation theorem. Earlier callees/MMIO/interrupts may affect the pointers, contents or frame. The source is liveS1, not automatically entryA0.

This scope proves the raw+52 relationship; separate config-layout/App evidence supplies field naming and actual construction. Stop after the post-copy destinationADDI. The remaining initializer, later functions, bulk stores and asynchronous writes are not inventoried as complete lifetime evidence. No actual callback body can be named from this review.

## Initialization and reference limits

Each actual30B zero helper and8B initializer AUIPC/JALR tail are reread. The numeric tail targetsRAM20000022; the unsigned-inclusive zero loop writeszero words with stride4, covering the callback word. This proves a conditional startup write only. It cannot identify installedRAM or a later value; the configuration copy is a concrete subsequent writer.

The bounded inventory examines every halfword offset of each retained contiguous segment for adjacent standard LUI20003+LW-to-word patterns:12 each. There are zero adjacent standard SB/SH/SW direct overlaps, zero exact LUI/ADDI-address pairs and zero complete U32LE address literals at any byte offset. These are syntactic patterns, not a wholeROM instruction-boundary/CFG or computed-reference absence proof. The bulk writer demonstrates why the distinction matters.

ledger.json records the eight-byte pattern witnesses and sourcePCs, the114B prefix,30B helper and8B tail. Pure operand decoding adds only encountered C.AND, standard32-bit JALR and conditional Xwchc QK_C_LHU forms. The existing pinned LLVM vendor definition does not prove installed physicalISA. Eight actual single-field byte controls reject: configdestination,copycount64,zero-storevalue,callback-load-offset per candidate. No legacy HOST matrix or CPU-state model is run.

## Replay

```sh
python3 -B check.py --project-root ROOT
python3 -B check.py --project-root ROOT \
  --firmware ID2966.bin --candidate-root EXISTING_WCH_REFERENCE
```

Default is metadata-only: actual_original_firmware_read=false and actual_candidate_sources_read=0. Both explicit flags produce false/true/2 and rerun eight controls. Both apk-analysis/tsl9-* and delivered analysis/* layouts work without archived builds. capture.py is create-only operand-data retention, not code generation.

Installed identity, callback identity/lifetime, actual App zero contents, ambient-A2 independence, fullABI, physicalFlash/NV ownership and OTA compatibility remain unproved. ABS40000 is a numeric witness, not a provider. Keep full8 and opaque-callee boundaries.
