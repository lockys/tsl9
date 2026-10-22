# Complete pre-copy comparison leaf200004BC

[繁體中文](readme.zh-TW.md)

**Under the specified candidate mapping, normal completion, valid memory/no adverse aliases/no asynchronous changes, this callee preservesS1/SP and config+52.** It is a complete62B/19instruction leaf, not an unknown nestedROMcall. This closes a local pre-copy preservation concern without proving installedidentity, App reachability or callbacklifetime.

| Candidate | Mapped sourceFlash | AnalysisRAM |
|---|---|---|
|V1.40/carrier|4076C..407AA|200004BC..200004FA|
|V1.31/carrier-dec2023|4072C..4076A|200004BC..200004FA|

Both complete bodies share SHA256 `39eff00fe85a0bdea780df359a1f1d1356681a168097a60b7b805faac6303581`. The firstRET at200004DE is **not** the function end: the following loop and second return1path end withRET200004F8. Nextbody is excluded.

The ledger retains both19-row field tables. Existing sealed callback-review supplies segment/HEX identities, initializationmapping and114B caller source. Explicit mode also reads official ID2966 SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667` and compares its308B originalApp config source with sealed evidence. No download/compiler/HOST/codegeneration or targetexecution occurs.

## Exact behavior

Before null/count tests: READ32 MMIO4002420C intoA5,WRITE32zero,FENCE.I. NullA0 or zeroA2 writes the savedword back and returnsA0=0. This is not vacuous-all-match=true or a purememcpy/memcmp interface.

For nonzeroA0/A2, A4=A0+A2 modulo32. Each loop incrementsA0, thenLBU A3,-1(A0), thenBNE A3,A1. **A1 is compared in full32bits**, with no low-byte truncation; A2 is also fullwidth. Any mismatch writes back savedMMIO and returns0. Only allspecifiedbytes equal to fullA1 reach the second writeback/return1. A1>255 therefore mismatches the first successfully read byte of a nonempty comparison. These0/1 results are not standardmemcmp sign semantics. There is no general accessible-range/overflow guard.

OnlyMMIO stores exist: initialzero plus two mutually exclusive savedword-writeback instructions. No config/payload/stack/heap store occurs. This proves requested writes, not restoration of all physicalMMIO sideeffects. ExplicitGPR destinations are onlyA0/A3/A4/A5; A1/A2/A6/A7/allS/GP/TP/SP/RA have no body writes. No frame, nestedcall or opaqueedge exists; all directbranches stay inside the62B leaf. Onnormalreturn A4=40024000,A5=the initialMMIOword; A3=lastreadbyte if a loop ran, otherwise incomingA3. RET uses rawRA with bit0masked.

## Caller correspondence

Both actual114B initializerprefixes match priorsealed fields. Entry+1C snapshotsconfigpointer inS1;+1A setsA2=6;+1E setsA1=255;+22 formsA0=config+24;the actual+28/+2C AUIPC/JALR target is200004BC. For validcallerdata this tests whether allsixbytes atconfig+24..29 areFF.

Afterreturn the caller setsA4=1,A5=3 andBEQ at+34 jumps toentry+D2 whenA0==1. That failureexit lies outside the prefix; this review records its target/currentvalues rather than inventing a complete epilogue contract. Return0 proceeds to read-only NVguards onliveS1+8/+56/+60; missingcallbacks can also branchto+D2 withA5=6. Passing/skippingNVchecks reaches+46 and the64B fill/copy sequence. These localguards do not writeS1/SP/config.

Thus the comparison and acceptedlocalguards preserve the config+52 value under normal/unaltered-code/noalias/noasync conditions. The existing46B fillleaf preservation proof is reused and its actualcandidatebody rechecked; the58B copyleaf remains in the sealed sourcechain. SuitableliveS0/S1, valid nonaliasing stack/code/MMIO and correctmapping/profile are required. This can carry an **existing** config+52 value into the copy; it does not independently establish zero, versiongate reachability or permanence. Laterinitializercontinuation/callbacks are outside thisscope.

## Replay

```sh
python3 -B check.py --project-root ROOT
python3 -B check.py --project-root ROOT \
  --firmware ID2966.bin --candidate-root EXISTING_WCH_REFERENCE
```

Default is metadata-only with actualcandidateleafreads=0. Both flags enable actualFWread,2leafbodies,2callerprefixes and2existingfillbodychecks. Eightactual single-field byte controls reject: nullgateGPR,fullA1comparisonGPR,successresult1,andcallerexpected255, perversion. No CPU-state/ISA execution or oldHOSTmatrix is used. Both apk-analysis/tsl9-* and deliveredanalysis/* layouts work without archivedbuilds;capture.py only creates operanddata once.

Installedidentity, wholeABI, completeinitializercontinuation, Appreachability, runtimecallbackvalue/lifetime andOTA remain unproved. No newBIN,network,hardware or physicalUIDread/transmission occurred.
