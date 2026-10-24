# Record processing and event scheduling

[繁體中文](README.md)

The new [C/C++ source](../../src/native/receive/record_control.c) covers original1798A–179FC: **114B/44 instructions/12 architectural regions**. Actual C11/C++17 objects preserve98 non-control bytes andsix typed references;data-only original-VA encoding matches all114B. [Evidence](evidence/standalone-trial.json)

## Static observations

- 1798E rejects unsignedA1>35 before allocating the32B frame.
- The zero-mode path passes sourceword[GP+100]+7*A1,destinationSP+8,length7 through tableword4004C. This establishes arguments/order,not installed callee identity.
- 179B2 reads fullwordSP+8 andextractsbits10..15. Maskbit0/bit1 conditionally updateGP+367/368 usingbit23 ofeach freshfullwordSP+12 read.
- 179D8 passesSP+8 directly to unresolved1787C andthen uses theshared32B restore.
- 179E4 storeslowA1 toGP+376 andpassesGP+379,event2,timeargument2 through40058 before thesharedrestore. No actual elapsed time ordevice action is claimed.

A7B argument doesnot justify narrowing native loads. ThefullwordSP+12 read includesSP+15 outside theseven-byte destination window; it is retained without invented initialization. GPfields are not named as seat ordo-not-disturb controls.

## Integration and limits

The original1798A reference binds thereal8B entry within thewhole114B. Theactual component has **2730B code+456B data,256 nonzeroFUNC regions,10 entry aliases,231 RELA and17 directUND**. All2616B parentcode,456B data and62 nonzero vector bindings remain intact. Resolving1798A exposes1787C,so theUND count stays17. [Native evidence](evidence/native-c.json) / [Provider ledger](pending-providers.json)

Default SDK table macros correspond to memcpy/start-task interfaces. Slot addresses are not function entries; installed ROM andABI remain unknown. [Profile](rom-profile-correspondence.json)

Selected sources now contain88 C/H files. Code-source comparisons122/244 objects pluspointer-data2/4 total **124/248**. Sourceprojection andoriginal-byte equality do not prove whole behavior. TheVMA-zero ET_REL component doesnot establish original placement,hardware/memory/ROM/startup/IRQ orBLE OTA compatibility.

## Next family and feature candidate

[Retained270B decode](next-1787c-frontier.json) spans1787C–1798A withentrycandidates1787C/178F8/17948. Thefirst range shows16-slot/7B-record queue characteristics andatail to17666; callback/private-register contracts need verification. An offline7B record inspector exposing raw masks,selectors andevent references could be useful; it remains aresearch candidate,not firmware functionality,with unknown field meanings kept numeric.

No target/HOST-model execution,ISA emulation,hardware/network access,newBIN,commit orpush. [Build receipt](evidence/integration-build.json) / [Publication provenance](publication-provenance.json)
