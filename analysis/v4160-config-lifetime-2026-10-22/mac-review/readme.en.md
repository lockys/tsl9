# Local footprint of original six-byte helper18F56

[繁體中文](readme.zh-TW.md)

**On its normal static path, original18F56 cannot clobberSP/S0 or explicitly write config callback bytesSP+68..71.** It is a complete50B/14instruction leaf with no nested or opaque call. This closes that particular callee concern, without proving earlier resident calls, actual configuration zero contents or the entire lifetime.

Official ID2966 SHA256: `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`, base8000. Helper18F56..18F88 is50B/14rows, SHA256 `5ea71cc5060b528919272111556388a084fe65e49474efa62683825e4df2eedf`. Caller19AAC..19AEE is66B/24rows, SHA256 `747ccb507745f07b46289b7fb200480c46f79ff63e399ce44e72042ac4ca421c`.

The initially read linkedELF is6ab2e06720dc9f9ea4fa531836605fed6d3b8832a7dfa008d76bd9bd0a54f7b2. Its AX/PROGBITS `.text.tsl9v4160.direct_expansion_18f56` hasaddress18F56,size50,alignment2; real GLOBAL FUNC `__tsl9v4160_call_18f56` has the sameaddress/size, and its50bytes equal the officialBIN. This is a bounded ELF view, not a whole-image build claim.

## Exact operations and preservation

18F56 setsA4=1FFFF000.18F5A reads32bits at1FFFF7E8 intoA5;18F62/66/70/74 sequentially store its four little-endian bytes atA0+0/1/2/3. Only afterward18F78 freshly reads32bits at1FFFF7EC;18F7C/82 store the low two bytes atA0+4/5. Do not replace this order with an unconditional eight-byte snapshot under arbitrary aliases.18F86 returns via JALR rd0,RA,0, clearing targetbit0 without writingRA.

OnlyA3/A4/A5 are explicitly written. A0/A1/A2/A6/A7/RA/SP/GP/TP/allS registers have no body writes. FinalA3=firstREAD32>>16,A4=1FFFF000,A5=secondREAD32>>8. There is no frame, internalbranch, nestedcallee or opaqueprovider. The numeric source addresses and extraction are confirmed; no physicalMAC/UID value was read, and a friendly function name does not establish an IEEE MAC source.

## Caller footprint

19AAC setsA0=currentSP+8;19AB4 JALrd1 calls18F56 with link19AB8. The helper preservesSP locally, and the continuation through19AEC has noSP/S/GP writes or intervening opaquecall.19AB8 setsA4=SP+16,indexA5=0,limitA3=6. The loop readsSP+8+index, incrementsindex andA4, then storesA2 atA4+23 and branchesuntilindex=6. Thus the six copy destinations areSP+16+(i+1)+23=SP+40..45, i.e.config+24..29. Helper destinations areSP+8..13.

The66B caller slice also contains19AAE SH atSP+48..49 and19AB2 SW atSP+64..67, with no otherstores. All explicit footprints excludeSP+68..71/config+52. This is closed-form arithmetic from verified fields, not CPU execution or instruction simulation.

The config guards at19AD2..19AE0 may self-loop, so reachinginit is conditional. On the accepted path,19AE2..19AEC freshly loadslotA4 fromnumeric40000 and callwithA0=SP+16. Effects of that nextcallee are outside this proof.

## Limits and replay

These local results assume the pinned code is followed with normally completing accesses/return, no asynchronous state changes or code-as-data mutation, and suitable memorymapping. Numeric disjointness does not measure physical mirroring/faults/hardware sideeffects. Earlier slot40048 or other resident effects, actualAppzero contents, installedidentity, callbacklifetime and fullABI/OTA remain unproved. Do not keep this resolved leaf described as an unknownROMcall, or extend its local proof to unrelated callees.

```sh
python3 -B check.py --project-root ROOT
python3 -B check.py --project-root ROOT --firmware ID2966.bin
python3 -B check.py --project-root ROOT --firmware ID2966.bin --image-elf IMAGE.elf
```

Default reports metadata_only=true and both actualreadflags false. ExplicitFW reads bothsource ranges and runs four actual single-field byte controls: sixth destinationbyte,rawRET sourceGPR,callerSP+8 offset,copydestinationoffset. Only explicitELF reports actual_helper_ELF_view_read=true, validating that bounded section/symbol/bytes rather than wholeELF provenance. Both apk-analysis/tsl9-* and delivered analysis/* layouts work without historicalbuilds. No compiler/HOST, targetexecution/emulation/ESIL, hardware, network or newBIN occurs.
