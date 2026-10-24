# Event consumer, retry callback and palette clues

[繁體中文](README.md)

The new [C/C++ source](../../src/native/receive/event_consumer.c) covers17666–1787C: **534B,187 instructions and35 architectural regions**. Actual C11/C++17 objects preserve472 non-control bytes and23 typed references;data-only original-VA encoding matches all534B. [Accepted receipt](evidence/standalone-trial.json)

Static observations include the16B entry's GP379/event1/time2 slot40058 call andconditional90B0 cancellation;the32B constructor's62B5 halfword,1753A call andconditional GP377/9124 retry;andthe48B handler's event-bit dispatch,queue updates only onzero results,fresh record reads andoriginal signed REM. Returned values andtime arguments are not physical success ormilliseconds.

Original1783A encodes table1AAE8. [Selected28B](selected-1aae8-data.json) contain seven little-endian words:

`000000FF, 00007DFF, 0000FFFF, 0000FF00, 00FFFF00, 00FF0000, 00FF00FF`

These24-bit constants andlater REM7 suggest a cycling palette. RGB/BGR/channel order andphysical lighting purpose remain unproved. User-defined seven-step palettes/offline previews are feature candidates,not implemented firmware. A later remainder doesnot bound theearlier lookup;these28B are not linked anddo not establish full table ownership/extent.

The actual17666 reference binds a24B entry within all534B. Existing90B0/9124 definitions are reused. New1753A/C776 dependencies increase direct UND from17 to18. The component has **3534B code+456B data,305 nonzero FUNC regions,12 aliases and261 RELA**;all3000B parent code,456B data and62 nonzero vector bindings remain intact. [Native evidence](evidence/native-c.json) / [Provider ledger](pending-providers.json)

Trial-v2 is accepted;trial-v1's shortened4B ADDI failed andits local outputs remain unclaimed. [SDK profile](rom-profile-correspondence.json) correspondence isnot installed ROM/ABI proof. Literal callbacks remain dependent onoriginal placement.

Selected sources contain90 C/H files:126 code-source comparisons/252 objects pluspointer-data2/4,total **128/256**. VMA-zero ET_REL doesnot prove a flashable image,installed ROM,memory,startup/IRQ,physical hardware orBLE OTA compatibility.

[Next1753A–17666 family](next-1753a-frontier.json) contains300B/103 instructions,two candidate entries andeight indirect calls. No target/HOST-model/ISA/ESIL execution,hardware/network access,newBIN,commit orpush occurred. [Build receipt](evidence/integration-build.json) / [Publication provenance](publication-provenance.json)
