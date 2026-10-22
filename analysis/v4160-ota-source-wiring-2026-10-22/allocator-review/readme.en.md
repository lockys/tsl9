# Slot 0x40070 candidates still forward ambient A2

[繁體中文](readme.zh-TW.md)

Actual static reads of the two existing SDK references do **not** prove allocation independent of the original S reply pointer. The wrapper and reviewed core prefix neither read nor write A2, but a conditional CFG path forwards it unchanged to a freshly loaded, unknown RAM callback. This cannot authorize narrowing the full8 bridge or claiming pointer nonescape.

## Original App and conditional mappings

Official ID2966 SHA256: `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`. This review rereads the90B at13B4C..13BA6 and compares every operand row with the sealed layout/reply-review ledger. At13B54 the original loads liveS1+70;13B60 setsA0=length;13B64 stores the source pointer at liveSP+12. A2 still carries that source pointer into13B68. A friendly allocator name or assumed prototype does not remove this physical argument.

| Existing reference | Slot40070 word | Wrapper Flash | Core Flash | Fresh fallback word |
|---|---|---|---|---|
| V1.40/carrier |20000236|404E6|402F0|RAM20003270|
| V1.31/carrier-dec2023 |20000236|404A6|402B0|RAM20003220|

The established resident-entry initialization evidence maps each wrapper to RAM20000236..2000028C. Actual original sparseHEX and capturedsegment hashes are checked. Each wrapper is86B/35instructions, SHA256 `dd02b794304fe9ae8b45e6cc3a888820393e679d5d3870a95a2a021fc0070faa`. Only110B/37instructions of the core atRAM20000040..200000AE are reviewed; this is not a complete allocator reconstruction.

## Operand-derived boundary

Wrapper: SP-=16, storesS1+4/S2+0/RA+12/S0+8 in that order; S1=40024000; readsMMIO+20C intoS2, writeszero and FENCE.I before the nullA0 test. For nonzeroA0: S0=A0; A0=low16(A0+8); A1=F000 OR S0; linkedcall atRAM2000026E targets20000040, link20000270. No explicit A2 read/write/store exists in the full wrapper.

Coreprefix uses another16B frame and S0/RA/MMIO save-zero-fence sequence. It rounds length to low16((A0+3)&~3), selects a list using threshold52, and compares listhead with sentinel. Equality leads to a fresh target load from the version-specific RAMword above; nonzeroA4 leads to JALR atRAM200000A0, link200000A2. Before this call A0=1, A1 OR(roundedLength<<16), and **A2 still carries its incoming value**. Actual reachability, callback contents and downstream observations are unknown. This is a field/CFG argument, not CPU-state execution or simulation.

Stop at this fresh indirect boundary. The other branch enters unreviewed allocation-search code atRAM200000AE; its inputs/termination/results are not inferred. Under a normally returning core with suitable live state, the wrapper writes32-bit zero atA0+0,16-bit liveS0 atA0+4,8-bitFF atA0+6, restoresMMIO, adds8 toA0 and freshly restoresRA/S0/S1/S2, popsSP andRET. Callee mutations, frame aliases, faults and interrupts can alter those operations. A conventional C ABI is not assumed. Null/failure paths have their own restoration and return behavior.

The two compressed stores are decoded under the existing LLVM HasVendorXwchc definitions:42a1=QK_C_SH S0,4(A0);7ca1=QK_C_SB A5,6(A0). The checker extracts quadrant/funct3/compactGPR/immediate independently; r2's floating-point display is not used as semantic evidence. This conditional candidate profile does not identify the installed chip ISA.

## Replay

```sh
python3 -B check.py --project-root ROOT
python3 -B check.py --project-root ROOT \
  --firmware ID2966.bin --candidate-root EXISTING_WCH_REFERENCE
```

Default is metadata-only with actual_original_firmware_read=false and actual_candidate_bodies_read=0. Supply both flags for actual originalApp plus four bounded candidate-body reads,196B per version, and eight actual single-field byte controls: linkedcorecall, headerlengthstore, fallbackslotoffset and indirecttargetGPR per version. Historical HOST matrices are not rerun. No archived W build is required; both apk-analysis/tsl9-* and delivered analysis/* evidence layouts work. capture.py only creates the retained operand ledger once; it generates no provider or firmware.

Installed resident/version/ISA, unknown callback behavior, ambient-register preservation, pointer nonescape, arbitrary aliases, fullABI, physicalFlash/NV ownership and wholeOTA remain unproved. The callback could inspect A2/callerframe, alter liveSP/S/GP/slots or fail to return. The next required evidence is the provider/initialization relationship for the RAM fallback word. This review stops there and retains full8/opaque-call boundaries. ABS40000 numeric witnesses are not resident implementations. No compilation, HOST run, target execution, ISA/ESIL stepping, hardware, network or newBIN occurred.
