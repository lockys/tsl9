# Resident providers and RF configuration evidence

[繁體中文](README.md)

The new [C/C++ source](../../src/native/receive/resident_providers.c) covers1753A–17666: **300B,103 instructions and12 architectural regions**. Actual C11/C++17 objects preserve298 non-control bytes andone typed branch;data-only original-VA encoding matches all300B. [Receipt](evidence/standalone-trial.json)

1753A retains A6/A7 private ports,the guard before its16B frame,GP366 sequence-field handling andfresh then-live S0+76/512/88/80 calls. The guard reads original2000C7A9 andreturns1;the normal path returns0,which is not physical RF TX success. The48B constructor175E8 retains original2000C7A0/268-byte arguments,task callback17476,stack32-byte arguments,configuration store order andliteral174EE.

## SDK/profile correspondence

Saved default slots correspond to memcpy,RF_SetChannel,start-task,set-event,memset,task registration andRF_Config. [Source lines andslots](rom-rf-profile-correspondence.json) Slots are not function entries,and actual calls use then-live S0 rather than assumed callee preservation.

The exact selected SDK callback typedef/struct declarations were compiled as C11/C++17 into **64B layout data with zero functions**. Both show rfConfig_t size32,alignment4 andmatching field offsets. The [public receipt](evidence/rf-layout.json) only normalizes CRLF toLF;the Windows original remains local,with equal JSON andboth digests recorded in publication provenance.

| Native stack write | Selected default SDK field |
| --- | --- |
| +0 halfword2501 | LLEMode1,Channel37 |
| +8 word8E89BED6 | accessAddress |
| +12 word00555555 | CRCInit |
| +16 word174EE | rfStatusCB original literal |
| +25 byte4 | HeartPeriod;physical timing unproved |

This supports software RF-configuration correspondence,not physical MCU/radio topology,installed ROM version,callee identity orABI. Layout data objects are diagnostic only andnot linked into firmware. No SDK function ormodule was executed.

## Integration and next work

The actual1753A reference binds its12B entry within all300B. The component contains **3834B code+456B data,317 nonzero FUNC regions,13 aliases,262 RELA and17 direct UND**. All3534B parent code,456B data and62 nonzero vector bindings remain intact. [Native evidence](evidence/native-c.json) / [Provider ledger](pending-providers.json)

Selected sources contain91 C/H files. Code-source128 comparisons/256 objects pluspointer-data2/4 total **130/260**;the two SDK layout objects are separate. VMA-zero ET_REL doesnot prove literal callback/original placement,installed ROM,memory,startup/IRQ,hardware orBLE OTA compatibility.

[NextRF callback candidates](../rf-callbacks-2026-10-24/corrected-frontier.json) span17476–1753A,196B/65 instructions. Aseparate [bounded C776 fragment](c776-bounded-backlog.json) is not claimed as acomplete function. Passive RF state/timeout diagnostics remain a future feature candidate requiring memory ownership/ABI evidence,not implemented firmware.

No target/HOST-model/ISA/ESIL execution,hardware/network access,newBIN,commit orpush. [Build receipt](evidence/integration-build.json) / [Publication provenance](publication-provenance.json)

Correction: the earlier manual callback calculation was16B early. Encoded AUIPC/ADDI now establish17476/174EE. The original212B candidate projection andnative receipts remain preserved;see the[correction record](../rf-callbacks-2026-10-24/literal-address-correction.json).
